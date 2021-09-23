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

    logging.info(f"CONFIGURACOES PROJETO: {str(projects_settings)}")

    projects_settings.update(custom_project_settings)

    if crawler_process:
        crawler = CrawlerProcess(projects_settings)
    else:
        crawler = CrawlerRunner(projects_settings)
        logging.info("EXECUTANDO RUNNER")

    # Senado Example
    # crawler.crawl(
    #     generic_scraper_pagination.ScraperPagination,
    #     root='https://www6g.senado.leg.br/busca',
    #     site_name='senado',
    #     search_steps=[
    #         {
    #             "elem_type": "input",
    #             "xpath": '//*[@id="busca-query"]',
    #             "action": {"write": "Povos e Comunidades Tradicionais"}
    #         },
    #         {
    #             "elem_type": "btn",
    #             "xpath": '//*[@id="search-addon"]/button',
    #             "action": {"click": True}
    #         },
    #     ],
    #     next_button_xpath='//*[@id="conteudoPrincipal"]/div/div[2]/div[2]/nav/ul/li[8]/a',
    #     allow_domains=['www12.senado.leg.br', 'www25.senado.leg.br'],
    #     allow=['noticias'],
    #     content_xpath={
    #         "content": "//*"
    #     },
    #     pagination_retries=3,
    #     pagination_delay=5,
    # )

    # running_process = crawler.crawl(
    #     mpf_scraper.MpfScraperSpider,
    #     keyword = "comunidades tradicionais"
    # )

    running_process = crawler.crawl(
        generic_scraper_pagination.ScraperPagination,
        root='http://www.mpf.mp.br/@@search',
        site_name='mpf',
        search_steps=[
            {
                "elem_type": "input",
                "xpath": '//*[@id="search-field"]/input[1]',
                "action": {"write": "Povos e Comunidades Tradicionais"}
            },
            {
                "elem_type": "btn",
                "xpath": '//*[@id="search-field"]/input[2]',
                "action": {"click": True}
            },
        ],
        next_button_xpath='//*[@id="search-results"]/div/span[2]/a',
        allow_domains=['www.mpf.mp.br'],
        restrict_xpaths='//*[@id="search-results"]/dl',
        allow=['pgr/noticias-pgr'],
        content_xpath={
            "content": "//*"
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
