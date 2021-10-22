import unittest
from ..spiders.mpf_scraper import MpfScraperSpider
from .responses.responses import fake_response_from_file


class OsdirSpiderTest(unittest.TestCase):

    def setUp(self):
        self.spider = MpfScraperSpider("quilombolas")

    def test_document_page_parse(self):
        url = (
            "http://www.mpf.mp.br/atuacao-tematica/ccr6/"
            "grupos-de-trabalho-1/quilombos/legislacao/"
            "decretos/07_02_2007.pdf/view"
        )

        results = self.spider.parse_document_page(
            fake_response_from_file(
                'fixtures/mpf_scraper/document_page.html',
                url
            ))

        expected_attributes = {
            "source": "mpf",
            "url": url,
            "title": (
                'Decreto de 07 de fevereiro de 2007 — 6ª Câmara - '
                'Populações Indígenas e Comunidades Tradicionais'
            )
        }

        self._test_recovered_attributes(results, expected_attributes)

    def _test_recovered_attributes(self, results, expected_attributes):

        for item in results:
            self.assertEquals(expected_attributes['source'], item['source'])
            self.assertEquals(expected_attributes['url'], item['url'])
            self.assertEquals(expected_attributes['title'], item['title'])
            self.assertIsNotNone(item['content'])
