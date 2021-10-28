import os
import unittest
from ..spiders.generic_crawler import GenericCrawlerSpider
from .responses.responses import fake_response_from_file
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

class GenericCrawlerTest(unittest.TestCase):
    
    
    def setUp(self):
        self.url = (
            "https://www.gov.br/incra/pt-br/assuntos/noticias/quilombolas-tratam-de-titulacao-e-acesso-a-creditos-com-gestores-do-incra-rs"
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
        results = self.crawler.parse_page(fake_response_from_file('fixtures/incra_scraper/document_page.html', self.url), "Quilombolas tratam de titulação e acesso a créditos com gestores do Incra/RS — Português (Brasil)", True)
        
        responses_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(responses_dir, 'responses/fixtures/incra_scraper/parsed_content.txt')
        file = open(file_path, 'r')

        expected_attributes = {
            "source": "incra",
            "url": self.url,
            "title": "Quilombolas tratam de titulação e acesso a créditos com gestores do Incra/RS — Português (Brasil)",
            "content": file.read()
        }
        file.close()

        for item in results:
            self.assertEquals(expected_attributes['source'], item['source'])
            self.assertEquals(expected_attributes['url'], item['url'])
            self.assertEquals(expected_attributes['title'], item['title'])
            self.assertIsNotNone(item['content'])
            self.assertEquals(expected_attributes['content'], item['content'])