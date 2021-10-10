# Create your tasks here

import sys
from celery import shared_task

sys.path.append('../pcts_scraper_jobs')
from run_scrapers import run_headless_scraper

@shared_task
def add(x, y):
    return x + y


@shared_task
def hello():
    return "Hello World!"


@shared_task
def run_scraper(scraper_id, keywords=[], **kwargs):
    run_headless_scraper(scraper_id, keywords)
    return True
