import os
import gc
import sys
import time

import scrapy
from scrapy.crawler import CrawlerRunner
from scrapy.spiders import Spider
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging

from twisted.internet import reactor
from multiprocessing.context import Process

from pcts_scrapers.spiders.mpf_scraper import MpfScraperSpider
from pcts_scrapers.spiders.incra_scraper import IncraScraperSpider

available_scrapers = {
    "MpfScraperSpider": MpfScraperSpider,
    "IncraScraperSpider": IncraScraperSpider,
}

keywords = [
    "povos e comunidades tradicionais",
    "quilombolas",
]

SELENIUM_DRIVER_ARGS_WITH_BROWSERVIEW = [
    '--no-sandbox',
    '--disable-gpu',
    '--javascript.enabled=False',
    'user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"'
]


def run_scrapers(choosen_scrapers=available_scrapers.keys(),
                 settings_file_path="pcts_scrapers.settings"):
    """ Execute Scrapy ScraperPagination spider
    Args:
        settings_file_path(str):    Filepath of Scrapy project settings.
            Example: "path.to.file.settings"
            Example: {"SPIDER_MODULES": ['path.to.file.spiders']}
    """

    print("EXECUTAR SCRAPER")
    os.environ.setdefault('SCRAPY_SETTINGS_MODULE', settings_file_path)

    projects_settings = get_project_settings()

    projects_settings['SELENIUM_DRIVER_ARGUMENTS'] = \
        SELENIUM_DRIVER_ARGS_WITH_BROWSERVIEW

    for scraper_id in choosen_scrapers:
        process_scraper_source = Process(
            target=run_scraper_source,
            args=(scraper_id, keywords, projects_settings)
        )
        process_scraper_source.start()
        process_scraper_source.join()


def run_scraper_source(scraper_id, keywords=[], projects_settings=get_project_settings()):
    scraper = available_scrapers[scraper_id]

    for keyword in keywords:
        print(f"=============================================")
        print(f"Scraping {scraper.name} source, Keyword: {keyword}")

        process_scraper_keyword = Process(
            target=run_scraper_keyword,
            args=(projects_settings, scraper, keyword)
        )
        process_scraper_keyword.start()
        process_scraper_keyword.join()

        print(f"Source {scraper.name} scraped")
        print(f"=============================================\n")


def run_headless_scraper(scraper_id, keywords=[], settings_file_path="pcts_scrapers.settings"):
    os.environ.setdefault('SCRAPY_SETTINGS_MODULE', settings_file_path)

    projects_settings = get_project_settings()

    run_scraper_source_flat(scraper_id, keywords, projects_settings)


def run_scraper_source_flat(scraper_id, keywords=[], projects_settings=get_project_settings()):
    scraper = available_scrapers[scraper_id]

    for keyword in keywords:
        print(f"=============================================")
        print(f"Scraping {scraper.name} source, Keyword: {keyword}")

        run_scraper_keyword(projects_settings, scraper, keyword)

        print(f"Source {scraper.name} scraped")
        print(f"=============================================\n")


def run_scraper_keyword(projects_settings, scraper: Spider, keyword=""):
    configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})
    crawler = CrawlerRunner(projects_settings)

    running_process = crawler.crawl(
        scraper,
        keyword=keyword
    )

    running_process.addBoth(lambda _: reactor.stop())
    reactor.run()


if __name__ == '__main__':
    try:
        run_scrapers()
    finally:
        gc.collect()
