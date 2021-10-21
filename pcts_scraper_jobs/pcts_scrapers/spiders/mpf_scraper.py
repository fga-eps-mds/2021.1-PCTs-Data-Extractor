import os
import re

from datetime import datetime
from scrapy.http import request
from ..items import ScraperItem
from time import sleep
from scrapy_selenium.http import SeleniumRequest
from scrapy_splash.request import SplashRequest
from scrapy import Request
from selenium.webdriver.chrome.webdriver import WebDriver
from scrapy.linkextractors import LinkExtractor
from scrapy.http.response.html import HtmlResponse
from scrapy.spiders import Spider


class PaginationException(Exception):
    pass


class MpfScraperSpider(Spider):
    name = 'mpf_scraper'
    source_name = 'mpf'
    allowed_domains = ['www.mpf.mp.br']
    allowed_paths = ['pgr/noticias-pgr', 'pgr/documentos', 'atuacao-tematica']
    restrict_xpaths = ('//*[@id="search-results"]/dl', )
    base_url = 'http://www.mpf.mp.br'  # NOSONAR
    content_xpath = '//*[@id="content"]'

    page_steps = 10
    pagination_retries = 5
    load_page_delay = 2
    pagination_delay = 10
    root_output_data_folder = f"{os.getcwd()}/output_data/"
    scraper_start_datetime = datetime.now().strftime('%Y%m%d_%H%M')

    def __init__(self, keyword=None, *args, **kwargs):
        self.logger.info("[Scraper MPF] Source")

        self.keyword = keyword
        self.source_url = f"{self.base_url}/@@search?SearchableText={self.keyword}"

        self.link_pages_extractor = LinkExtractor(
            allow=(self.allowed_paths),
            allow_domains=(
                self.allowed_domains),
            restrict_xpaths=(
                self.restrict_xpaths),
            canonicalize=False,
            unique=True,
            process_value=None,
            deny_extensions=None,
            strip=True
        )

    def start_requests(self, *args, **kwargs):
        yield SeleniumRequest(url=(self.source_url),
                              callback=(self.parse_home_pagination),
                              meta={'donwload_timeout': self.load_page_delay})

    def parse_home_pagination(self, response: HtmlResponse):
        driver: WebDriver = response.request.meta['driver']

        # Parse result list page
        found_urls = []
        old_found_urls = []
        page = 0

        while True:
            page += 1
            pagination_content_retrieved = False
            for retry in range(self.pagination_retries):
                try:
                    self.logger.info(f"Page: {page},\tRetry: {retry + 1}")
                    sleep(self.pagination_delay)
                    response = self.get_current_page_response(driver)
                    # Get links and call inner pages
                    old_found_urls = found_urls
                    found_urls = self.get_page_links(response)

                    # Pagination stop condition
                    if found_urls == old_found_urls:
                        raise PaginationException(
                            "Old and new urls are the same")

                    if len(found_urls) > 0:
                        for url in found_urls:
                            self.logger.info("Pagina Encontrada: " + url)

                            # yield SplashRequest(
                            #     url=url,
                            #     callback=self.parse_document_page,
                            #     endpoint='render.html',
                            #     args={'wait': self.load_page_delay},
                            # )

                            yield Request(
                                url=url,
                                callback=self.parse_document_page,
                                meta={'donwload_timeout': self.load_page_delay}
                            )

                            sleep(0.1)
                    pagination_content_retrieved = True
                    break
                except PaginationException as e:
                    self.logger.info(str(e))

            if not pagination_content_retrieved:
                raise PaginationException("End of Pagination")

            # =========== Follow next Pagination
            # b_start:int=10
            if page == 1:
                next_button = driver.find_element_by_xpath(
                    '//*[@id="search-results"]/div/span[1]/a')
            else:
                next_button = driver.find_element_by_xpath(
                    '//*[@id="search-results"]/div/span[2]/a')

            # click the button to go to next page
            driver.execute_script("arguments[0].click();", next_button)
        driver.close()

    def parse_document_page(self, response: HtmlResponse):
        page_content = ScraperItem()
        page_content['source'] = self.source_name
        page_content['url'] = response.url
        page_content['title'] = response.xpath(
            '/html/head/title/text()').extract_first()

        res = response.xpath(self.content_xpath).extract()
        page_content['content'] = '\n'.join(
            (elem for elem in res)).strip().replace('<br>', '\n')
        page_content['content'] = re.sub(
            r'\<.*?\>|\\t|\s\s', '', page_content['content'])

        self.logger.info('Pagina Carregada:' + response.url)

        yield page_content

    def get_current_page_response(self, driver: WebDriver):
        return HtmlResponse(url=(driver.current_url),
                            body=(driver.find_element_by_xpath(
                                '//*').get_attribute('outerHTML')),
                            encoding='utf-8')

    def get_page_links(self, response):
        links = self.link_pages_extractor.extract_links(response)
        str_links = []
        for link in links:
            str_links.append(link.url)

        return str_links
