import os
import gc
import logging

import scrapy
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.utils.project import get_project_settings

from twisted.internet import reactor

from .pcts_scrapers.spiders import generic_scraper_pagination

# import importlib.machinery

# generic_scraper_pagination = importlib.machinery.SourceFileLoader('modulename','/app/scrapers/pcts_scrapers/spiders/generic_scraper_pagination.py').load_module()


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

    logging.info(f"CONFIGURACOES PROJETO: {str(projects_settings)}")

    projects_settings.update(custom_project_settings)

    if crawler_process:
        crawler = CrawlerProcess(projects_settings)
    else:
        crawler = CrawlerRunner(projects_settings)
        logging.info("EXECUTANDO RUNNER")

    # TCU Example
    running_process = crawler.crawl(
        generic_scraper_pagination.ScraperPagination,
        root='https://pesquisa.apps.tcu.gov.br',
        site_name='tcu',
        search_steps=[
            {
                "elem_type": "input",
                "xpath": '//*[@id="termo"]',
                "action": {"write": "Povos e Comunidades Tradicionais"}
            },
            {
                "elem_type": "btn",
                "xpath": '//*[@id="container-campo-pesquisa"]/div/div[1]/div[5]/div/button',
                "action": {"click": True}
            },
        ],
        next_button_xpath='//*[@id="container"]/div[2]/div/div/header/div[2]/mat-paginator/div/div/div[2]/button[2]',
        allow_domains=['pesquisa.apps.tcu.gov.br'],
        allow=['#/documento'],
        pagination_retries=3,
        pagination_delay=10,
    )

    crawler.join()

    if crawler_process:
        crawler.start(stop_after_crawl=True)
    else:
        running_process.addBoth(lambda _: reactor.stop())
        reactor.run(0)


# if __name__ == '__main__':
#     try:
#         run_scraper()
#     finally:
#         gc.collect()
