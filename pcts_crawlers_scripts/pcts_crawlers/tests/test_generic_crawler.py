import os
import unittest
from ..spiders.generic_crawler import GenericCrawlerSpider
from .responses.responses import fake_response_from_file
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

class GenericCrawlerTest(unittest.TestCase):
    
    
    def setUp(self):
        pass

    def test_document_page_parse_from_incra(self):
        url = (
            "https://www.gov.br/incra/pt-br/assuntos/noticias/quilombolas-tratam-de-titulacao-e-acesso-a-creditos-com-gestores-do-incra-rs"
        )
        crawler = GenericCrawlerSpider(
            url_root=url,
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

        results = crawler.parse_page(fake_response_from_file('fixtures/incra/document_page.html', url), "Quilombolas tratam de titulação e acesso a créditos com gestores do Incra/RS — Português (Brasil)", True)
        
        responses_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(responses_dir, 'responses/fixtures/incra/parsed_content.txt')
        file = open(file_path, 'r')

        expected_attributes = {
            "source": "incra",
            "url": url,
            "title": "Quilombolas tratam de titulação e acesso a créditos com gestores do Incra/RS — Português (Brasil)",
            "content": file.read()
        }
        file.close()

        self._test_recovered_attributes(results, expected_attributes)
        

    def test_document_page_parse_from_mpf(self):
        url = (
            "http://www.mpf.mp.br/atuacao-tematica/ccr6/grupos-de-trabalho-1/quilombos/legislacao/decretos/07_02_2007.pdf/view"
        )
        crawler = GenericCrawlerSpider(
            url_root=url,
            site_name="mpf",
            allowed_domains=[
                "www.mpf.mp.br"
            ],
            allowed_paths=[
                "pgr/noticias-pgr",
                "pgr/documentos",
                "atuacao-tematica"
            ],
            qs_search_keyword_param="SearchableText",
            keyword="quilombolas"
        )

        results = crawler.parse_page(fake_response_from_file('fixtures/mpf/document_page.html', url), "Decreto de 07 de fevereiro de 2007 — 6ª Câmara - Populações Indígenas e Comunidades Tradicionais", True)
        
        responses_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(responses_dir, 'responses/fixtures/mpf/parsed_content.txt')
        file = open(file_path, 'r')

        expected_attributes = {
            "source": "mpf",
            "url": url,
            "title": "Decreto de 07 de fevereiro de 2007 — 6ª Câmara - Populações Indígenas e Comunidades Tradicionais",
            "content": file.read()
        }
        file.close()

        self._test_recovered_attributes(results, expected_attributes)

    def _test_recovered_attributes(self, results, expected_attributes):
        for item in results:
            self.assertEqual(expected_attributes['source'], item['source'])
            self.assertEqual(expected_attributes['url'], item['url'])
            self.assertEqual(expected_attributes['title'], item['title'])
            self.assertIsNotNone(item['content'])
            self.assertEqual(expected_attributes['content'], item['content'])