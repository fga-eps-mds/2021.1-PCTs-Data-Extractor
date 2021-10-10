# Create your tasks here

import sys

from celery import Celery
from celery import shared_task, task
from celery.schedules import crontab

sys.path.append('../pcts_scraper_jobs')
from run_scrapers import run_headless_scraper

@shared_task(name="mpf_scraper")
def mpf_scraper(keywords, **kwargs):
    run_headless_scraper("MpfScraperSpider", keywords)
    return True


@shared_task(name="incra_scraper")
def incra_scraper(keywords, **kwargs):
    run_headless_scraper("IncraScraperSpider", keywords)
    return True


# def run_template_scraper(scraper_name):
#     @shared_task(name=scraper_name)
#     def template_scraper(scraper_id, keywords=[], **kwargs):
#         run_headless_scraper(scraper_id, keywords)
#         return True
