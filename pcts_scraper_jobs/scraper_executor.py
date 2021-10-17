import os
import gc
import sys
import time

import scrapy
from scrapy.crawler import CrawlerRunner, CrawlerProcess
from scrapy.spiders import Spider
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging

from twisted.internet import reactor
from multiprocessing.context import Process

from pcts_scrapers.spiders.mpf_scraper import MpfScraperSpider
from pcts_scrapers.spiders.incra_scraper import IncraScraperSpider


from scrapy import signals

available_scrapers = {
    "MpfScraperSpider": MpfScraperSpider,
    "IncraScraperSpider": IncraScraperSpider,
}

keywords = [
    "povos e comunidades tradicionais",
    "quilombolas",
]

def callback(spider, reason):
    stats = spider.crawler.stats.get_stats()  # stats is a dictionary

    print("========================= METRICAS =========================")
    print("METRICAS:")
    print(stats)
    print("========================= METRICAS =========================")

    # write stats to the database here

    reactor.stop()



def run_scraper(scraper_id, keyword, settings_file_path="pcts_scrapers.settings"):
    configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})
    print("=======================================================================")
    print(f"INICIAR SCRAPER {scraper_id}. KEYWORD: {keyword}")
    os.environ.setdefault('SCRAPY_SETTINGS_MODULE', settings_file_path)
    projects_settings = get_project_settings()
    scraper = available_scrapers[scraper_id]

    # Scraper run
    crawler = CrawlerProcess(projects_settings)
    crawler_instance = crawler.create_crawler(scraper)

    running_process = crawler.crawl(
        crawler_instance,
        keyword=keyword
    )

    crawler.start()

    stats = crawler_instance.stats.get_stats()
    print("========================= METRICAS =========================")
    print("METRICAS:")
    print(stats)
    print("========================= METRICAS =========================")

    # running_process.addBoth(lambda _: reactor.stop())
    # reactor.run()
    print("=======================================================================")

    return stats


if __name__ == '__main__':
    try:
        run_scraper(scraper_id="IncraScraperSpider", keyword=keywords[0])
    finally:
        gc.collect()
