# Create your tasks here

import sys
import os

from celery import Celery
from celery import shared_task, task
from celery.schedules import crontab
from celery.canvas import group, chain, chord

if (os.environ.get("PROJECT_ENV_EXECUTOR", default="HOST") == "DOCKER"):
    sys.path.append('/app/pcts_scraper_jobs')
else:
    sys.path.append('../pcts_scraper_jobs')

from scraper_executor import run_scraper


# @shared_task(name="mpf_scraper")
# def mpf_scraper(keywords, **kwargs):
#     run_scraper("MpfScraperSpider", keywords)
#     return True

@shared_task(name="mpf_scraper_keyword")
def mpf_scraper_keyword(keyword, **kwargs):
    run_scraper(
        "MpfScraperSpider", keyword
    )
    return True


@shared_task(name="mpf_scraper_group")
def mpf_scraper_group(keywords, **kwargs):
    mpf_scraper_keywords = [
        mpf_scraper_keyword.subtask(kwargs={"keyword": keyword}, immutable=True)
        for keyword in keywords
    ]

    result = chain(*mpf_scraper_keywords).apply_async()

    return True


@shared_task(name="incra_scraper_keyword")
def incra_scraper_keyword(keyword, **kwargs):
    run_scraper(
        "IncraScraperSpider", keyword
    )
    return True


@shared_task(name="incra_scraper_group")
def incra_scraper_group(keywords, **kwargs):
    incra_scraper_keywords = [
        incra_scraper_keyword.subtask(kwargs={"keyword": keyword}, immutable=True)
        for keyword in keywords
    ]

    result = chain(*incra_scraper_keywords).apply_async()

    return True


# def run_template_scraper(scraper_name):
#     @shared_task(name=scraper_name)
#     def template_scraper(scraper_id, keywords=[], **kwargs):
#         run_scraper(scraper_id, keywords)
#         return True
