import scrapy
from scrapy.crawler import CrawlerProcess

from generic_scraper.spiders.url_extractor import UrlExtractor
from generic_scraper.spiders.scraper import Scraper
from generic_scraper.spiders.scraper_pagination import ScraperPagination

from generic_scraper.settings import SELENIUM_DRIVER_NAME
from generic_scraper.settings import SELENIUM_DRIVER_EXECUTABLE_PATH
from generic_scraper.settings import SELENIUM_DRIVER_ARGUMENTS
from generic_scraper.settings import DOWNLOADER_MIDDLEWARES

# Settings to call spider by python script
SELENIUM_CUSTOM_SETTINGS = {
  'SELENIUM_DRIVER_NAME': SELENIUM_DRIVER_NAME,
  'SELENIUM_DRIVER_EXECUTABLE_PATH': SELENIUM_DRIVER_EXECUTABLE_PATH,
  'SELENIUM_DRIVER_ARGUMENTS': SELENIUM_DRIVER_ARGUMENTS,
  'DOWNLOADER_MIDDLEWARES': DOWNLOADER_MIDDLEWARES,
}

from shutil import which
from os import getcwd

def main():
    process = CrawlerProcess(SELENIUM_CUSTOM_SETTINGS)

    process.crawl(
        ScraperPagination,
        root='https://pesquisa.apps.tcu.gov.br/#/pesquisa/todas-bases',
        allow_domains='pesquisa.apps.tcu.gov.br',
        allow=['/#/documento'],
        search_input_xpath='//*[@id="mat-input-0"]',
        next_button_xpath='//*[@id="container"]/div[2]/div/div/header/div[2]/mat-paginator/div/div/div[2]/button[2]',
        article_page_wait_element_xpath='//*[@id="tipo_processo"]',
        called_by_python_script=True
    )
    process.start()

if __name__ == '__main__':
    main()
