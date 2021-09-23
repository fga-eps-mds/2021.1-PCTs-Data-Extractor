from scrapy.spiders import Spider
import scrapy
from scrapy.http import response
from scrapy import Request


class MpfScraperSpider(Spider):
    name = 'mpf_scraper'
    site_name = "mpf"
    content_start = 0
    allowed_domains = ['www.mpf.mp.br']
    start_urls = [
        'http://www.mpf.mp.br/@@search?SearchableText=comunidades+tradicionais&path=']

    def __init__(self, keyword=None):
        self.source = 'http://www.mpf.mp.br/@@search?SearchableText='
        self.keyword = keyword

    def start_requests(self, *args, **kwargs):
        yield Request(
            url=self.source + self.keyword + "&b_start:int=" + self.content_start,
            callback=self.parse
        )

    def parse(self, response):
        site_response = {
            "source": self.site_name,
            "url": response.url,
            "title": response.xpath("/html/head/title/text()").extract_first(),
            "content": response.body.decode("utf-8")
        }
        print(
            "----------------------------------------------------------------------------")
        print(site_response["url"])
        print(
            "----------------------------------------------------------------------------")
        print(site_response["title"])
        print(
            "----------------------------------------------------------------------------")
        print(site_response["content"])
        print(
            "----------------------------------------------------------------------------")
        yield site_response
