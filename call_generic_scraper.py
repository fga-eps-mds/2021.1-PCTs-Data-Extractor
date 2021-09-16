import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from pcts_scrapers.spiders.generic_scraper_pagination import ScraperPagination

def run_scraper():
    crawler = CrawlerProcess(get_project_settings())

    # TCU Example
    crawler.crawl(
        ScraperPagination,
        root='https://pesquisa.apps.tcu.gov.br',
        site_name='tcu',
        next_button_xpath='//*[@id="container"]/div[2]/div/div/header/div[2]/mat-paginator/div/div/div[2]/button[2]',
        called_by_python_script=True,
        allow_domains=['pesquisa.apps.tcu.gov.br'],
        allow=['#/documento'],
        pagination_retries=3,
    )

    # # Senado Example
    # crawler.crawl(
    #     ScraperPagination,
    #     root='https://www6g.senado.leg.br/busca/?q=comunidades+tradicionais&colecao=Not%C3%ADcias&p=45',
    #     site_name='senado',
    #     next_button_xpath='//*[@id="conteudoPrincipal"]/div/div[2]/div[2]/nav/ul/li[8]/a',
    #     called_by_python_script=True,
    #     allow_domains=['www12.senado.leg.br','www25.senado.leg.br'],
    #     allow=['noticias'],
    # )

    crawler.join()
    crawler.start(stop_after_crawl=True)

if __name__ == '__main__':
    run_scraper()
