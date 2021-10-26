import os
import re

from scrapy.spiders import Spider
from scrapy.linkextractors import LinkExtractor
from scrapy.link import Link
from scrapy.http.response.html import HtmlResponse
from scrapy_selenium import SeleniumRequest
from scrapy.selector.unified import Selector
from scrapy import Request

from scrapy_splash import SplashRequest

from ..items import CrawlerItem

SCRAPY_REQUEST_METHOD = os.environ.get('SCRAPY_REQUEST_METHOD', default="SPLASH")
DEFAULT_TITLE_XPATH = "/html/head/title/text()"
DEFAULT_ALL_CONTENT_XPATH = (
    "//body//*//text()[not(ancestor::script) and not(ancestor::noscript) and not(ancestor::style) and not(ancestor::header)]"
)
DEFAULT_CONTENT_XPATH = (
    "//body//*//text()[not(ancestor::script) and not(ancestor::noscript) and "
    "not(ancestor::style) and not(ancestor::header) and not(ancestor::footer) and "
    "not(ancestor::nav) and not(ancestor::menu) and not(ancestor::aside) and "
    "not(ancestor::dialog) and not(ancestor::form) and not(ancestor::a) and "
    "not(ancestor::ul) and not(ancestor::li) and not(ancestor::label)]"
)


class GenericCrawlerSpider(Spider):
    """ Generic Crawler for use on paginated item listing page of the target website
    """

    name = 'generic-crawler'
    start_urls = []

    def __init__(self, url_root, site_name, allowed_domains=None, allowed_paths=None,
                 qs_search_keyword_param=None, contains_end_path_keyword=False, retries=1,
                 page_load_timeout=2, keyword="", *args, **kwargs):
        """ Initializes GenericCrawlerSpider

        Args:
            url_root(str): root page url
            site_name(str): site name
            allowed_domains(list<str>): url domains allowed to be crawled
            allowed_paths(list<str>): url paths allowed to be crawled
            qs_search_keyword_param(str): query string param where the keyword should be imputed
            retries(int): number of attempts to crawled page
            page_load_timeout(int): time limit to load page
            keyword(str): word or expression used to search the first page or check affinity
            *args: Extra arguments
            **kwargs: Extra named arguments
        """
        self.logger.info("Generic Crawler Source: %s", url_root)
        self.source_url = url_root
        self.site_name = site_name
        self.allowed_domains = allowed_domains
        self.allowed_paths = allowed_paths
        self.qs_search_keyword_param = qs_search_keyword_param
        self.contains_end_path_keyword = contains_end_path_keyword
        self.retries = retries
        self.page_load_timeout = page_load_timeout
        self.keyword = keyword
        self.start_urls.append(self.source_url)
        self.search_page = True

        self.link_pages_extractor = LinkExtractor(
            allow_domains=self.allowed_domains,
            allow=self.allowed_paths,
            canonicalize=False,
            unique=True,
            process_value=lambda url: url.strip(" /"),
            deny_extensions=None,
            strip=True,
        )

    def start_requests(self, *args, **kwargs):
        self.define_stats_attributes()

        end_path = ""
        query_string = ""
        if self.contains_end_path_keyword:
            end_path = "/" + str(self.keyword)
        if self.qs_search_keyword_param:
            query_string = f"?{str(self.qs_search_keyword_param)}={str(self.keyword)}"
        entrypoint_url = self.source_url + end_path + query_string

        self.logger.info(f"ENTRYPOINT URL: {entrypoint_url}")

        yield self.make_request(entrypoint_url, 'INITIAL_SEARCH_PAGE')

    def parse_page(self, response: HtmlResponse, title):
        # self.logger.info(f"PARSE PAGE: {response.url}")

        # Extracao de todo o conteudo da pagina
        # Para buscar afinidade com o conteudo na pagina
        # ou a partir dos links
        all_content_list = response.xpath(
            DEFAULT_ALL_CONTENT_XPATH
        ).extract()
        all_content = '\n'.\
            join(elem for elem in all_content_list).strip()

        # Follow Links
        if self.check_keyword_affinity(all_content):
            links_found = self.get_page_links(response)

            for link in links_found:
                yield self.make_request(link['url'], link['text'])
            yield self.data_extraction(response, title)
        else:
            self.stats.inc_value('dropped_records_by_keyword_all_content')

    def define_stats_attributes(self):
        self.stats = self.crawler.stats

        self.stats.set_value(
            'dropped_records_by_keyword_all_content',
            0
        )
        self.stats.set_value(
            'dropped_records_by_keyword_restrict_content',
            0
        )

    def make_request(self, url, title):
        if SCRAPY_REQUEST_METHOD == "SPLASH":
            return SplashRequest(
                url=url,
                callback=self.parse_page,
                endpoint='render.html',
                args={'wait': self.page_load_timeout},
                cb_kwargs={"title": title}
            )
        else:
            return Request(
                url=url,
                callback=self.parse_page,
                meta={'download_timeout': self.page_load_timeout},
                cb_kwargs={"title": title}
            )

    def data_extraction(self, response: HtmlResponse, title):
        # Extracao restrita a apenas as partes importantes
        # do conteudo da pagina
        restrict_content_list = response.xpath(
            DEFAULT_CONTENT_XPATH
        ).extract()

        restrict_content = '\n'.\
            join(elem for elem in restrict_content_list).strip()

        if self.check_keyword_affinity(restrict_content):
            page_content = CrawlerItem()
            page_content['source'] = self.site_name
            page_content['url'] = response.url.strip(" /")
            if title:
                page_content['title'] = title
            else:
                page_content['title'] = response.xpath(
                    DEFAULT_TITLE_XPATH
                ).extract_first()
            page_content['content'] = restrict_content
            return page_content
        else:
            self.stats.inc_value(
                'dropped_records_by_keyword_restrict_content'
            )

    def check_keyword_affinity(self, content: str):
        return re.search(self.keyword, content, flags=re.IGNORECASE)

    def get_page_links(self, response):
        links = self.link_pages_extractor.extract_links(response)
        str_links = []
        for link in links:
            str_links.append({
                "url": link.url,
                "text": link.text
            })
        return str_links