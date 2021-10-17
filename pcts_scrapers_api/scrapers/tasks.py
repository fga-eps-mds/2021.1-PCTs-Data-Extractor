# Create your tasks here

import sys
import os

from celery import Celery
from celery import shared_task, task
from celery.schedules import crontab
from celery.canvas import group, chain, chord
from pcts_scrapers_api.celery import app as celery_app

if (os.environ.get("PROJECT_ENV_EXECUTOR", default="HOST") == "DOCKER"):
    sys.path.append('/app/pcts_scraper_jobs')
else:
    sys.path.append('../pcts_scraper_jobs')

from scraper_executor import run_scraper

from scrapers.models import Scraper

# from scrapers.models import ScraperExecutionGroup
# from scrapers.models import ScraperExecution


def task_scraper_group_wrapper(task_group_name, task_sub_prefix_name):
    @task(name=task_sub_prefix_name)
    def task_scraper_subtask(scraper_classname, keyword, **kwargs):
        run_scraper(scraper_classname, keyword)
        return True

    @task(name=task_group_name)
    def task_scraper_group(scraper_classname, keywords, **kwargs):
        task_scraper_subtasks = [
            task_scraper_subtask.subtask(
                kwargs={
                    "keyword": keyword,
                    "scraper_classname": scraper_classname
                },
                immutable=True
            )
            for keyword in keywords
        ]
        result = chain(*task_scraper_subtasks).apply_async()
        return True

    return task_scraper_group


# ============================= AUTO CREATE SCHEDULERS ON STARTUP
@celery_app.on_after_finalize.connect
def setup_periodic_scrapers(sender: Celery, **kwargs):
    KEYWORDS = [
        "povos e comunidades tradicionais",
        "quilombolas",
    ]
    print("ADICIONANDO PERIODIC TASKS")

    DEFAULT_SCRAPERS = [
        {"id": 1, "class": "MpfScraperSpider"},
        {"id": 2, "class": "IncraScraperSpider"},
    ]

    for scraper_config in DEFAULT_SCRAPERS:
        scraper = Scraper.objects.get(pk=scraper_config["id"])

        sender.add_periodic_task(
            crontab(minute='0', hour='4', day_of_week='*',
                    day_of_month='*', month_of_year='*'),
            task_scraper_group_wrapper(
                scraper.task_name_prefix,
                f"{scraper.task_name_prefix}_keyword",
            ).subtask(kwargs={
                "keywords": KEYWORDS,
                "scraper_classname": scraper_config["class"],
            }),
            name=scraper.task_name_prefix,
        )
