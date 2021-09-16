import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from pcts_scrapers.spiders.generic_scraper_pagination import ScraperPagination


def run_scraper():
    crawler = CrawlerProcess(get_project_settings())

    # TCU Example
    # crawler.crawl(
    #     ScraperPagination,
    #     root='https://pesquisa.apps.tcu.gov.br',
    #     site_name='tcu',
    #     search_steps=[
    #         {
    #             "elem_type": "input",
    #             "xpath": '//*[@id="termo"]',
    #             "action": {"write": "Povos e Comunidades Tradicionais"}
    #         },
    #         {
    #             "elem_type": "btn",
    #             "xpath": '//*[@id="container-campo-pesquisa"]/div/div[1]/div[5]/div/button',
    #             "action": {"click": True}
    #         },
    #     ],
    #     next_button_xpath='//*[@id="container"]/div[2]/div/div/header/div[2]/mat-paginator/div/div/div[2]/button[2]',
    #     allow_domains=['pesquisa.apps.tcu.gov.br'],
    #     allow=['#/documento'],
    #     pagination_retries=3,
    #     pagination_delay=10,
    # )

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
    crawler.crawl(
        ScraperPagination,
        root='https://www.in.gov.br/consulta/-/buscar/',
        site_name='diario_oficial',
        search_steps=[
            {
                "elem_type": "input",
                "xpath": '//*[@id="search-bar"]',
                "action": {"write": "Povos e Comunidades Tradicionais"}
            },
            {
                "elem_type": "btn",
                "xpath": '//*[@id="toggle-search-advanced"]',
                "action": {"click": True}
            },
            {
                "elem_type": "btn",
                "xpath": '//*[@id="search-advanced"]/div[1]/div[1]/div[1]/div[2]/label',
                "action": {"click": True}
            },
            {
                "elem_type": "btn",
                "xpath": '//*[@id="div-search-bar"]/div/div/div/i',
                "action": {"click": True}
            },
        ],
        next_button_xpath='//*[@id="rightArrow"]',
        allow_domains=['www.in.gov.br'],
        allow=['web/dou'],
        pagination_retries=3,
        pagination_delay=5,
    )

    crawler.join()
    crawler.start(stop_after_crawl=True)


if __name__ == '__main__':
    run_scraper()
