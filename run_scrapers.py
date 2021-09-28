import os
import gc

import scrapy
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.spiders import Spider
from scrapy.utils.project import get_project_settings

from twisted.internet import reactor

from pcts_scrapers.spiders import mpf_scraper
from pcts_scrapers.spiders import incra_scraper

scrapers = [
    mpf_scraper.MpfScraperSpider,
    incra_scraper.IncraScraperSpider,
]

keywords = [
    "povos e comunidades tradicionais",
    "quilombolas",
]


def run_scrapers(settings_file_path="pcts_scrapers.settings", custom_project_settings={},
                 crawler_process=True):
    """ Execute Scrapy ScraperPagination spider
    Args:
        settings_file_path(str):    Filepath of Scrapy project settings.
            Example: "path.to.file.settings"
        custom_project_settings(str):   Customm Attributes settings to update default project settings.
            Example: {"SPIDER_MODULES": ['path.to.file.spiders']}
    """

    print("EXECUTAR SCRAPER")
    os.environ.setdefault('SCRAPY_SETTINGS_MODULE', settings_file_path)

    projects_settings = get_project_settings()

    projects_settings.update(custom_project_settings)

    for scraper in scrapers:
        run_scraper(projects_settings, scraper, keywords, crawler_process)


def run_scraper(projects_settings, scraper: Spider, keywords: [],
                crawler_process=True):
    for keyword in keywords:
        print(f"=============================================")
        print(f"Scraping {scraper.name} source")

        if crawler_process:
            crawler = CrawlerProcess(projects_settings)
        else:
            crawler = CrawlerRunner(projects_settings)

        running_process = crawler.crawl(
            scraper,
            keyword=keyword
        )

        crawler.join()

        if crawler_process:
            crawler.start(stop_after_crawl=True)
        else:
            running_process.addBoth(lambda _: reactor.stop())
            reactor.run(0)
        
        print(f"Source {scraper.name} scraped")
        print(f"=============================================\n")


if __name__ == '__main__':
    try:
        run_scrapers()
    finally:
        gc.collect()
