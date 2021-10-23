from time import sleep
import os
import json
from datetime import datetime
import re
import unicodedata
import logging

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

from ..items import ScraperItem
from scrapy.utils.log import configure_logging


class PaginationException(Exception):
    pass


class GenericScraperSpider(Spider):
    """ Generic Scraper for use on paginated item listing page of the target website
    """

    name = 'generic-scraper'
    start_urls = []

    def __init__(self, url_root=None, site_name=None, query_string_params=None, js_search_steps=None,
                 next_button_xpath=None, content_xpath=None, pagination_retries=1, pagination_delay=1,
                 page_load_timeout=2, keyword="", *args, **kwargs):
        """ Initializes GenericScraperSpider

        Args:
            url_root(str): root page url
            site_name(str): site name
            js_search_steps(list<dict>): steps to generate the documents result list
            next_button_xpath(str): XPATH of "Next" button of the listing page
            *args: Extra arguments
            **kwargs: Extra named arguments
        """
        configure_logging(install_root_handler=True)
        logging.disable(20)  # CRITICAL = 50
        self.logger.info(
            "[Scraper Pagination] Source: %s Kwargs: %s",
            url_root, kwargs
        )
        self.source_url = url_root
        self.site_name = site_name
        self.query_string_params = query_string_params
        self.js_search_steps = js_search_steps
        self.next_button_xpath = next_button_xpath
        self.content_xpath = content_xpath
        self.pagination_retries = pagination_retries
        self.pagination_delay = pagination_delay
        self.page_load_timeout = page_load_timeout
        self.keyword = keyword
        self.options = kwargs

        self.search_by_url = True if query_string_params else False

        GenericScraperSpider.start_urls.append(self.source_url)
        GenericScraperSpider.allowed_domains = self.options.get('allowed_domains')
        self.link_pages_extractor = LinkExtractor(
            allow=self.options.get('allowed_paths'),
            deny=self.options.get('deny'),
            allow_domains=self.options.get('allowed_domains'),
            deny_domains=self.options.get('deny_domains'),
            restrict_xpaths=self.options.get('restrict_xpaths'),
            canonicalize=False,
            unique=True,
            process_value=None,
            deny_extensions=None,
            restrict_css=self.options.get('restrict_css'),
            strip=True,
        )

        super(GenericScraperSpider, self).__init__(*args, **kwargs)

    def start_requests(self, *args, **kwargs):
        if self.search_by_url:
            # home_url = f'{self.source_url}?{"&".join(str(param["param"]) + "=" + str(param["value"]) for param in self.query_string_params)}'
            home_url = f'{self.source_url}?{"&".join(str(param["param"]) + "=" + str(self.keyword) for param in self.query_string_params)}'
        else:
            home_url = self.source_url

        yield SeleniumRequest(
            url=home_url,
            callback=self.parse_home_pagination,
            meta={'donwload_timeout': self.pagination_delay}
            # wait_time=self.pagination_delay,
            # wait_until=EC.visibility_of_all_elements_located(
            #     (By.XPATH, self.js_search_steps[0]["xpath"])),
        )

    def parse_home_pagination(self, response: HtmlResponse):
        driver: WebDriver = response.request.meta['driver']

        self.execute_js_search_steps(driver)

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
                            print("Pagina Encontrada:", url)

                            # yield SplashRequest(
                            #     url=url,
                            #     callback=self.parse_document_page,
                            #     endpoint='render.html',
                            #     args={'wait': self.page_load_timeout},
                            # )

                            yield Request(
                                url=url,
                                callback=self.parse_document_page,
                                meta={'donwload_timeout': self.page_load_timeout}
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
        page_content = ScraperItem()

        page_content['source'] = self.site_name
        page_content['url'] = response.url
        page_content['title'] = response.xpath(
            "/html/head/title/text()").extract_first()

        # Extracao de conteudo baseado no mapeamento passado em content_xpath
        for content_key in self.content_xpath:
            if self.content_xpath[content_key]:
                res = response.xpath(self.content_xpath[content_key]).extract()
                page_content[content_key] = '\n'.join(
                    elem for elem in res).strip()

        # Exemplo manual
        # page_content['content'] = response.body.decode("utf-8")

        print("Pagina Carregada:", response.url)

        yield page_content

    def execute_js_search_steps(self, driver: WebDriver):
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

        if self.js_search_steps:
            for search_step in self.js_search_steps:
                elem = driver.find_element_by_xpath(search_step["xpath"])

                action_type = ACTION_TYPES[search_step["elem_type"]]

                search_step_value = search_step["action"][action_type["type"]]

                action = action_type["action"]

                # Substitui valor
                if action_type["need_value"]:
                    action = action.replace("${VALUE}", self.keyword)

                driver.execute_script(action, elem)

                sleep(1)

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
