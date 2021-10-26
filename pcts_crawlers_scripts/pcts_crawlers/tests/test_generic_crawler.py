import unittest
from ..spiders.generic_crawler import GenericCrawlerSpider
from .responses.responses import fake_response_from_file
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

class GenericCrawlerTest(unittest.TestCase):
    
    
    def setUp(self):
        self.url = (
            "https://www.gov.br/incra/pt-br/assuntos/noticias/"
            "quilombolas-tratam-de-titulacao-e-acesso-a-creditos"
            "-com-gestores-do-incra-rs"
        )
        self.crawler = GenericCrawlerSpider(
            url_root=self.url,
            site_name="incra",
            allowed_domains=[
                "www.gov.br"
            ],
            allowed_paths=[
                "incra/pt-br/assuntos/noticias",
                "incra/pt-br/assuntos/governanca-fundiaria"
            ],
            qs_search_keyword_param="SearchableText",
            keyword="quilombolas"
            )
        

    def test_document_page_parse_from_incra(self):
        results = self.crawler.parse_page(fake_response_from_file('fixtures/incra_scraper/document_page.html', self.url), "test")
        for item in results:
            print("===============================START=================================")
            print(item)
            print("================================================================")
            print(item['source'])
            print("================================================================")
            print(item['url'])
            print("================================================================")
            print(item['title'])
            print("================================================================")
            print(item['content'])
            print("================================================================")