import os
import gc
import logging

import scrapy
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.utils.project import get_project_settings

from twisted.internet import reactor

if os.environ.get('PROJECT_ENV_EXECUTOR') == 'DOCKER':
    from .pcts_scrapers.spiders import generic_scraper_pagination
else:
    from pcts_scrapers.spiders import generic_scraper_pagination


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

    # Senado Example
    # crawler.crawl(
    #     ScraperPagination,
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
    #     pagination_retries=3,
    #     pagination_delay=5,
    # )

    # Diario Oficial
    # crawler.crawl(
    #     ScraperPagination,
    #     root='https://www.in.gov.br/consulta/-/buscar/',
    #     site_name='diario_oficial',
    #     search_steps=[
    #         {
    #             "elem_type": "input",
    #             "xpath": '//*[@id="search-bar"]',
    #             "action": {"write": "Povos e Comunidades Tradicionais"}
    #         },
    #         {
    #             "elem_type": "btn",
    #             "xpath": '//*[@id="toggle-search-advanced"]',
    #             "action": {"click": True}
    #         },
    #         {
    #             "elem_type": "btn",
    #             "xpath": '//*[@id="search-advanced"]/div[1]/div[1]/div[1]/div[2]/label',
    #             "action": {"click": True}
    #         },
    #         {
    #             "elem_type": "btn",
    #             "xpath": '//*[@id="div-search-bar"]/div/div/div/i',
    #             "action": {"click": True}
    #         },
    #     ],
    #     next_button_xpath='//*[@id="rightArrow"]',
    #     allow_domains=['www.in.gov.br'],
    #     allow=['web/dou'],
    #     pagination_retries=3,
    #     pagination_delay=5,
    # )

    crawler.join()

    if crawler_process:
        crawler.start(stop_after_crawl=True)
    else:
        running_process.addBoth(lambda _: reactor.stop())
        reactor.run(0)


if os.environ.get('PROJECT_ENV_EXECUTOR') != 'DOCKER':
    if __name__ == '__main__':
        try:
            run_scraper(logging=logging)
        finally:
            gc.collect()
