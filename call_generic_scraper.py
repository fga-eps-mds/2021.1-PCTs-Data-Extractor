import scrapy
from scrapy.crawler import Crawler, CrawlerRunner, CrawlerProcess

from generic_scraper.spiders.generic_scraper_pagination import ScraperPagination

from generic_scraper.settings import BOT_NAME
from generic_scraper.settings import SPIDER_MODULES
from generic_scraper.settings import NEWSPIDER_MODULE
from generic_scraper.settings import DEFAULT_REQUEST_HEADERS
from generic_scraper.settings import ROBOTSTXT_OBEY

from generic_scraper.settings import SELENIUM_DRIVER_NAME
from generic_scraper.settings import SELENIUM_DRIVER_EXECUTABLE_PATH
from generic_scraper.settings import SELENIUM_DRIVER_ARGUMENTS

from generic_scraper.settings import DUPEFILTER_CLASS
from generic_scraper.settings import HTTPCACHE_STORAGE
from generic_scraper.settings import SPLASH_URL
from generic_scraper.settings import DOWNLOADER_MIDDLEWARES
from generic_scraper.settings import SPIDER_MIDDLEWARES

from scrapy.utils.project import get_project_settings


# Settings to call spider by python script
CUSTOM_SETTINGS = {
  'BOT_NAME': BOT_NAME,
  'SPIDER_MODULES': SPIDER_MODULES,
  'NEWSPIDER_MODULE': NEWSPIDER_MODULE,
  'DEFAULT_REQUEST_HEADERS': DEFAULT_REQUEST_HEADERS,
  'ROBOTSTXT_OBEY': ROBOTSTXT_OBEY,
  'SELENIUM_DRIVER_NAME': SELENIUM_DRIVER_NAME,
  'SELENIUM_DRIVER_EXECUTABLE_PATH': SELENIUM_DRIVER_EXECUTABLE_PATH,
  'SELENIUM_DRIVER_ARGUMENTS': SELENIUM_DRIVER_ARGUMENTS,
  'DUPEFILTER_CLASS': DUPEFILTER_CLASS,
  'HTTPCACHE_STORAGE': HTTPCACHE_STORAGE,
  'SPLASH_URL': SPLASH_URL,
  'DOWNLOADER_MIDDLEWARES': DOWNLOADER_MIDDLEWARES,
  'SPIDER_MIDDLEWARES': SPIDER_MIDDLEWARES,
}

from shutil import which
from os import getcwd

def main():
    crawler = CrawlerProcess(get_project_settings())

    crawler.crawl(
        ScraperPagination,
        root='https://pesquisa.apps.tcu.gov.br/#/resultado/todas-bases/quilombolas?ts=1631452168640&pb=jurisprudencia-selecionada',
        site_name='tcu',
        next_button_xpath='//*[@id="container"]/div[2]/div/div/header/div[2]/mat-paginator/div/div/div[2]/button[2]',
        called_by_python_script=True,
        allow_domains=['pesquisa.apps.tcu.gov.br'],
        allow=['#/documento'],
    )
    crawler.join()
    crawler.start(stop_after_crawl=True)

if __name__ == '__main__':
    main()
