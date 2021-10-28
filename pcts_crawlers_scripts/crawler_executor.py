import os
import gc
import sys
import time

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging

from twisted.internet import reactor
from multiprocessing.context import Process

from pcts_crawlers.spiders.generic_crawler import GenericCrawlerSpider

keywords = [
    "povos e comunidades tradicionais",
    "quilombolas",
]


def run_generic_crawler(crawler_args, keyword, settings_file_path="pcts_crawlers.settings"):
    configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})
    print("=======================================================================")
    print(f"INICIAR CRAWLER {crawler_args['site_name']}. KEYWORD: {keyword}")
    os.environ.setdefault('SCRAPY_SETTINGS_MODULE', settings_file_path)
    projects_settings = get_project_settings()

    # Crawler run
    crawler = CrawlerProcess(projects_settings)
    crawler_instance = crawler.create_crawler(GenericCrawlerSpider)

    crawler.crawl(
        crawler_instance,
        **crawler_args,
        keyword=keyword
    )

    crawler.start()

    stats = crawler_instance.stats.get_stats()
    stats["keyword"] = keyword

    print("========================= METRICAS =========================")
    print("METRICAS:")
    print(stats)
    print("========================= METRICAS =========================")

    return stats


if __name__ == '__main__':
    try:
        crawler_args = {
            "site_name": "incra",
            "task_name_prefix": "incra_crawler",
            "url_root": "https://www.gov.br/incra/pt-br/search",
            "qs_search_keyword_param": "SearchableText",
            "allowed_domains": [
                "www.gov.br"
            ],
            "allowed_paths": [
                "incra/pt-br/assuntos",
                "incra/pt-br/search"
            ],
            "retries": 3,
            "page_load_timeout": 5,
            "cron_minute": "0",
            "cron_hour": "3",
            "cron_day_of_week": "*",
            "cron_day_of_month": "*",
            "cron_month_of_year": "*",
            "contains_dynamic_js_load": True,
            "created_at": "2021-10-17T19:26:54.660443"
        }

        # crawler_args = {
        #     "site_name": "icmbio",
        #     "task_name_prefix": "icmbio_crawler",
        #     "url_root": "https://www.icmbio.gov.br/portal/busca",
        #     "qs_search_keyword_param": "searchword",
        #     "allowed_domains": [
        #         "icmbio.gov.br"
        #     ],
        #     "allowed_paths": [
        #         "portal"
        #     ],
        #     "retries": 3,
        #     "page_load_timeout": 3,
        #     "cron_minute": "0",
        #     "cron_hour": "6",
        #     "cron_day_of_week": "*",
        #     "cron_day_of_month": "*",
        #     "cron_month_of_year": "*",
        #     "contains_dynamic_js_load": False,
        #     "created_at": "2021-10-17T19:26:54.660443"
        # }

        run_generic_crawler(crawler_args, keyword="quilombolas")
    finally:
        gc.collect()
