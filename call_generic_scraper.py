import os
import gc
import logging

import scrapy
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.utils.project import get_project_settings

from twisted.internet import reactor

from pcts_scrapers.spiders import generic_scraper_pagination, mpf_scraper


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

    # running_process = crawler.crawl(
    #     mpf_scraper.MpfScraperSpider,
    #     keyword = "comunidades tradicionais"
    # )

    running_process = crawler.crawl(
        generic_scraper_pagination.ScraperPagination,
        root='https://www.gov.br/incra/pt-br/search',
        site_name='incra',
        query_string_params=[
            {
                "param": "SearchableText",
                "value": "quilombolas"
            }
        ],
        # js_search_steps=[
        #     {
        #         "elem_type": "input",
        #         "xpath": '//*[@id="searchtext-input"]',
        #         "action": {"write": "quilombolas"}
        #     },
        #     {
        #         "elem_type": "btn",
        #         "xpath": '//*[@id="searchtext-label"]/button',
        #         "action": {"click": True}
        #     },
        # ],
        next_button_xpath='//*[@id="search-results"]/div[4]/div[2]/span[2]/ul[2]/li[3]/a',
        allow_domains=['www.gov.br'],
        allow_path=['incra/pt-br/assuntos/noticias'],
        restrict_xpaths='//*[@id="search-results"]/div[4]/div[2]/span[2]/ul[1]/li',
        content_xpath={
            "content": '//body//*//text()',
            # "content": '//*[@id="parent-fieldname-text"]/div/*/text()',
        },
        pagination_retries=3,
        pagination_delay=5,
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
