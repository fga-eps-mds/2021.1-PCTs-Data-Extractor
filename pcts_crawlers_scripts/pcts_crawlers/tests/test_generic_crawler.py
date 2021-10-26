import unittest
from ..spiders.generic_crawler import GenericCrawlerSpider
from .responses.responses import fake_response_from_file
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

class GenericCrawlerTest(unittest.TestCase):
    
    
    def setUp(self):
        crawler_args = {
            "site_name": "incra",
            "task_name_prefix": "incra_crawler",
            "url_root": "https://www.gov.br/incra/pt-br/search",
            "qs_search_keyword_param": "SearchableText",
            "allowed_domains": [
                "www.gov.br"
            ],
            "allowed_paths": [
                "incra/pt-br/assuntos/noticias",
                "incra/pt-br/assuntos/governanca-fundiaria"
            ],
            "retries": 3,
            "page_load_timeout": 3,
            "created_at": "2021-10-17T19:26:54.660443"
        }
        keyword="quilombolas"

        projects_settings = get_project_settings()
        crawler = CrawlerProcess(projects_settings)
        crawler_instance = crawler.create_crawler(GenericCrawlerSpider)

        crawler.crawl(
            crawler_instance,
            **crawler_args,
            keyword=keyword
        )

    def test_document_page_parse(self):
        pass