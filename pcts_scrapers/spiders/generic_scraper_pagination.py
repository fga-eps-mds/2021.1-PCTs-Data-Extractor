from time import sleep
import os
import json
from datetime import datetime
import re
import unicodedata

from scrapy.spiders import CrawlSpider, Rule, Spider
from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.http.response.html import HtmlResponse
from scrapy_selenium import SeleniumRequest
from scrapy.selector.unified import Selector

from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from scrapy_splash import SplashRequest

from ..items import GenericScraperPaginationItem

DEFAULT_ROOT_OUTPUT_DATA_FOLDER = f"{os.getcwd()}/output_data/"


class PaginationException(Exception):
    pass


class ScraperPagination(Spider):
    """ Generic Scraper for use on paginated item listing page of the target website
    """

    name = 'generic-scraper-pagination'
    root_output_data_folder = DEFAULT_ROOT_OUTPUT_DATA_FOLDER
    scraper_start_datetime = datetime.now().strftime("%Y%m%d_%H%M")
    start_urls = []

    def __init__(self, root=None, site_name=None, search_steps=None, next_button_xpath=None,
                 content_xpath=None, pagination_retries=1, pagination_delay=1, *args, **kwargs):
        """ Initializes ScraperPagination

        Args:
            root(str): root page url
            site_name(str): site name
            search_steps(list<dict>): steps to generate the documents result list
            next_button_xpath(str): XPATH of "Next" button of the listing page
            *args: Extra arguments
            **kwargs: Extra named arguments
        """
        self.logger.info("[Scraper Pagination] Source: %s Kwargs: %s",
                         root, kwargs)
        self.source = root
        self.site_name = site_name
        self.search_steps = search_steps
        self.next_button_xpath = next_button_xpath
        self.content_xpath = content_xpath
        self.pagination_retries = pagination_retries
        self.pagination_delay = pagination_delay
        self.options = kwargs

        ScraperPagination.start_urls.append(root)
        ScraperPagination.allowed_domains = self.options.get('allow_domains')
        self.link_pages_extractor = LinkExtractor(
            allow=self.options.get('allow'),
            deny=self.options.get('deny'),
            allow_domains=self.options.get('allow_domains'),
            deny_domains=self.options.get('deny_domains'),
            restrict_xpaths=self.options.get('items_xpath'),
            canonicalize=False,
            unique=True,
            process_value=None,
            deny_extensions=None,
            restrict_css=self.options.get('restrict_css'),
            strip=True,
        )

        self.output_folder_path = os.path.join(
            self.root_output_data_folder,
            self.site_name,
            self.scraper_start_datetime,
        )

        super(ScraperPagination, self).__init__(*args, **kwargs)

    def start_requests(self, *args, **kwargs):
        yield SeleniumRequest(
            url=self.source,
            callback=self.parse_home_pagination,
            # wait_time=5,
            # wait_until=EC.visibility_of_all_elements_located(
            #     (By.XPATH, self.search_steps[0]["xpath"])),
        )

    def parse_home_pagination(self, response: HtmlResponse):
        driver: WebDriver = response.request.meta['driver']

        self.execute_search_steps(driver)

        # Parse result list page
        found_urls = []
        old_found_urls = []
        page = 0

        while True:
            page += 1
            pagination_content_retrieved = False
            for retry in range(self.pagination_retries):
                try:
                    print(f"Page: {page},\tRetry: {retry + 1}")
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
                            print({
                                "link": url,
                                "source": dict(source=self.source)
                            })
                            yield SplashRequest(
                                url=url,
                                callback=self.parse_document_page,
                                endpoint='render.html',
                                args={'wait': 1},
                            )

                            sleep(0.1)
                    pagination_content_retrieved = True
                    break
                except PaginationException as e:
                    print(str(e))
                    # break

            if not pagination_content_retrieved:
                raise Exception("End of Pagination")

            # =========== Follow next Pagination
            next_button = driver.find_element_by_xpath(
                self.next_button_xpath)
            # click the button to go to next page
            driver.execute_script("arguments[0].click();", next_button)
        driver.close()

    def parse_document_page(self, response: HtmlResponse):
        page_content = GenericScraperPaginationItem()

        page_content['url'] = response.url
        page_content['title'] = response.xpath("/html/head/title/text()").extract_first()

        # Extracao de conteudo baseado no mapeamento passado em content_xpath
        for content_key in self.content_xpath:
            res = response.xpath(self.content_xpath[content_key]).extract()
            page_content[content_key] = '\n'.join(elem for elem in res).strip()
        # Exemplo manual
        # page_content['content'] = response.body.decode("utf-8")

        print("Pagina Carregada:", response.url)

        yield page_content

    def execute_search_steps(self, driver: WebDriver):
        INPUT_ACTION = {
            "need_value": True,
            "type": "write",
            "action": "arguments[0].value = '${VALUE}';",
        }

        BTN_ACTION = {
            "need_value": False,
            "type": "click",
            "action": "arguments[0].click();",
        }

        ACTION_TYPES = {
            "input": INPUT_ACTION,
            "btn": BTN_ACTION,
        }

        for search_step in self.search_steps:
            elem = driver.find_element_by_xpath(search_step["xpath"])

            action_type = ACTION_TYPES[search_step["elem_type"]]

            search_step_value = search_step["action"][action_type["type"]]

            action = action_type["action"]

            # Substitui valor
            if action_type["need_value"]:
                action = action.replace("${VALUE}", search_step_value)

            driver.execute_script(action, elem)

            sleep(1)

        # =============== Example of a plain list of steps

        # search_input = driver.find_element_by_xpath('//*[@id="termo"]')

        # driver.execute_script("arguments[0].value = 'Povos e Comunidades Tradicionais';", search_input)
        # # search_input.send_keys('Povos e Comunidades Tradicionais')

        # search_button = driver.find_element_by_xpath(
        #     '//*[@id="container-campo-pesquisa"]/div/div[1]/div[5]/div/button')

        # driver.execute_script("arguments[0].click();", search_button)
        # search_button.click()

    def get_current_page_response(self, driver: WebDriver):
        return HtmlResponse(
            url=driver.current_url,
            body=driver.find_element_by_xpath(
                '//*').get_attribute("outerHTML"),
            encoding='utf-8'
        )

    def get_page_links(self, response):
        links = self.link_pages_extractor.extract_links(response)
        str_links = []
        for link in links:
            str_links.append(link.url)
        return str_links

    def save_body_page(self, driver: WebDriver):
        body_page = driver.find_element_by_xpath(
            '//*').get_attribute("outerHTML")

        with open("page_crawled.html", "w") as f:
            f.write(body_page)
