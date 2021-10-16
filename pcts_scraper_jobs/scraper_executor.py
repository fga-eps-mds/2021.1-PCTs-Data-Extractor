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

def run_scraper(scraper_id, keyword, settings_file_path="pcts_scrapers.settings"):
    print("=======================================================================")
    print(f"INICIAR SCRAPER {scraper_id}. KEYWORD: {keyword}")
    os.environ.setdefault('SCRAPY_SETTINGS_MODULE', settings_file_path)
    projects_settings = get_project_settings()
    scraper = available_scrapers[scraper_id]

    run_scraper_keyword(projects_settings, scraper, keyword)
    print("=======================================================================")


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
        run_scraper(scraper_id="MpfScraperSpider", keyword=keywords[0])
    finally:
        gc.collect()
