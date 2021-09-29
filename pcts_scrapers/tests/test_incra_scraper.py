import unittest
from pcts_scrapers.spiders.incra_scraper import IncraScraperSpider
from .responses.responses import fake_response_from_file


class OsdirSpiderTest(unittest.TestCase):

    def setUp(self):
        self.spider = IncraScraperSpider("quilombolas")

    def test_document_page_parse(self):
        url = (
            "https://www.gov.br/incra/pt-br/assuntos/noticias/"
            "quilombolas-tratam-de-titulacao-e-acesso-a-creditos"
            "-com-gestores-do-incra-rs"
        )

        results = self.spider.parse_document_page(
            fake_response_from_file(
                'fixtures/incra_scraper/document_page.html',
                url
            ))

        expected_attributes = {
            "source": "incra",
            "url": url,
            "title": (
                "Quilombolas tratam de titulação e acesso a "
                "créditos com gestores do Incra/RS — Português (Brasil)"
            )
        }

        self._test_recovered_attributes(results, expected_attributes)

    def _test_recovered_attributes(self, results, expected_attributes):

        for item in results:
            self.assertEquals(expected_attributes['source'], item['source'])
            self.assertEquals(expected_attributes['url'], item['url'])
            self.assertEquals(expected_attributes['title'], item['title'])
            self.assertIsNotNone(item['content'])
