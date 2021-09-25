import os
import gc
import logging

import scrapy
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.utils.project import get_project_settings

from twisted.internet import reactor

from pcts_scrapers.spiders import mpf_scraper


def run_scraper(settings_file_path="pcts_scrapers.settings", custom_project_settings={}, crawler_process=True, logging=logging.basicConfig()):
    """ Execute Scrapy ScraperPagination spider
    Args:
        settings_file_path(str):    Filepath of Scrapy project settings.
            Example: "path.to.file.settings"
        custom_project_settings(str):   Customm Attributes settings to update default project settings.
            Example: {"SPIDER_MODULES": ['path.to.file.spiders']}
    """

    logging.info("EXECUTAR SCRAPER")
    os.environ.setdefault('SCRAPY_SETTINGS_MODULE', settings_file_path)

    projects_settings = get_project_settings()

    projects_settings.update(custom_project_settings)

    if crawler_process:
        crawler = CrawlerProcess(projects_settings)
    else:
        crawler = CrawlerRunner(projects_settings)
        logging.info("Crawler RUNNER")

    running_process = crawler.crawl(
        mpf_scraper.MpfScraperSpider,
        keyword="povos e comunidades tradicionais"
    )

    crawler.join()

    if crawler_process:
        crawler.start(stop_after_crawl=True)
    else:
        running_process.addBoth(lambda _: reactor.stop())
        reactor.run(0)


if __name__ == '__main__':
    try:
        run_scraper(logging=logging)
    finally:
        gc.collect()
