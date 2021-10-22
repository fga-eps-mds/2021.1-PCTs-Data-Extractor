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
from pcts_scrapers.spiders.generic_scraper import GenericScraper


from scrapy import signals

available_scrapers = {
    "MpfScraperSpider": MpfScraperSpider,
    "IncraScraperSpider": IncraScraperSpider,
}

keywords = [
    "povos e comunidades tradicionais",
    "quilombolas",
]


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
    stats["keyword"] = keyword

    print("========================= METRICAS =========================")
    print("METRICAS:")
    print(stats)
    print("========================= METRICAS =========================")

    # running_process.addBoth(lambda _: reactor.stop())
    # reactor.run()
    return stats


def run_generic_scraper(scraper_id, scraper_args, keyword, settings_file_path="pcts_scrapers.settings"):
    configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})
    print("=======================================================================")
    print(f"INICIAR SCRAPER {scraper_id}. KEYWORD: {keyword}")
    os.environ.setdefault('SCRAPY_SETTINGS_MODULE', settings_file_path)
    projects_settings = get_project_settings()
    scraper = GenericScraper

    # Scraper run
    crawler = CrawlerProcess(projects_settings)
    crawler_instance = crawler.create_crawler(scraper)

    running_process = crawler.crawl(
        crawler_instance,
        **scraper_args,
        keyword=keyword
    )

    crawler.start()

    stats = crawler_instance.stats.get_stats()
    stats["keyword"] = keyword

    print("========================= METRICAS =========================")
    print("METRICAS:")
    print(stats)
    print("========================= METRICAS =========================")

    # running_process.addBoth(lambda _: reactor.stop())
    # reactor.run()
    return stats


if __name__ == '__main__':
    try:
        # run_scraper(scraper_id="IncraScraperSpider", keyword=keywords[0])

        # Scraper Generico
        senado_args = {
            "root": 'https://www6g.senado.leg.br/busca',
            "site_name": 'senado',
            "js_search_steps": [
                {
                    "elem_type": "input",
                    "xpath": '//*[@id="busca-query"]',
                    "action": {"write": "Povos e Comunidades Tradicionais"}
                },
                {
                    "elem_type": "btn",
                    "xpath": '//*[@id="search-addon"]/button',
                    "action": {"click": True}
                },
            ],
            "next_button_xpath": '//*[@id="conteudoPrincipal"]/div/div[2]/div[2]/nav/ul/li[8]/a',
            "allow_domains": ['www12.senado.leg.br', 'www25.senado.leg.br'],
            "allow_path": ['noticias'],
            "content_xpath": {
                "content": '//body//*//text()',
            },
            "pagination_retries": 3,
            "pagination_delay": 5,
        }

        incra_args = {
            "root": 'https://www.gov.br/incra/pt-br/search?SearchableText=quilombolas',
            "site_name": 'incra',
            "js_search_steps": [
                {
                    "elem_type": "btn",
                    "xpath": ('//*[@id="search-results"]/div[contains(@class, "govbr-tabs")]/'
                              'div[contains(@class, "swiper-wrapper")]/div[last()]//a'),
                    "action": {"click": True}
                },
            ],
            "next_button_xpath": '//*[@id="search-results"]//ul[contains(@class, "paginacao")]/li[last()]//a',
            "allow_domains": ['www.gov.br'],
            "allow_path": [
                'incra/pt-br/assuntos/noticias',
                'incra/pt-br/assuntos/governanca-fundiaria'
            ],
            "restrict_xpaths": [
                '//*[@id="search-results"]//ul[contains(@class, "searchResults")]//a'
            ],
            "content_xpath": {
                "content": '//body//*//text()',
            },
            "pagination_retries": 5,
            "pagination_delay": 10,
        }

        run_generic_scraper("GenericScraper", incra_args, keyword=keywords[0])
    finally:
        gc.collect()
