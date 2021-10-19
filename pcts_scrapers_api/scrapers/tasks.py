# Create your tasks here

import sys
import os

from datetime import datetime
from celery import Celery
from celery.app import task as task_obj
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

from scrapers.models import ScraperExecutionGroup
from scrapers.models import ScraperExecution
from scrapers.models import STATUS_CHOICES


def task_scraper_group_wrapper(task_group_name, task_sub_prefix_name):
    """ Wrapper do task group de execucao de um scraper ionteiro
        e a subtask de execucao de uma keyword por vez
    """

    @task(name=task_sub_prefix_name, bind=True)
    def task_scraper_subtask(self, scraper_classname, scraper_execution_group_id,
                             keyword, **kwargs):
        scraper_execution_group = ScraperExecutionGroup.objects.get(
            pk=scraper_execution_group_id)

        task_id = self.request.id
        task_instance = celery_app.AsyncResult(task_id)
        result_meta = task_instance._get_task_meta()
        task_name = result_meta.get("task_name")

        print("ATRIBUTOS TASK EXEC")
        print("TASK_EXEC_ID:", self.request.id)
        print("TASK_EXEC_INSTANCE_NAME:", task_name)

        # Start execution monitoring
        scraper_execution = ScraperExecution.objects.create(
            scraper_execution_group=scraper_execution_group,
            task_id=task_id,
            task_name=task_name,
            keyword=keyword,
            status=STATUS_CHOICES[0][0]
        )

        try:
            execution_stats = run_scraper(scraper_classname, keyword)

            # Update execution monitoring on success
            scraper_execution.finish_datetime = datetime.now()
            scraper_execution.status = STATUS_CHOICES[1][0]
            scraper_execution.scraped_pages = execution_stats.get(
                "downloader/request_count")
            scraper_execution.saved_records = execution_stats.get(
                "saved_records")
            scraper_execution.dropped_records = execution_stats.get(
                "droped_records")
        except Exception as e:
            # Update execution monitoring on fail
            scraper_execution.finish_datetime = datetime.now()
            scraper_execution.status = STATUS_CHOICES[2][0]

        scraper_execution.save()
        return True

    @task(name=task_group_name, bind=True)
    def task_scraper_group(self, scraper_classname, scraper_id, keywords, **kwargs):
        scraper = Scraper.objects.get(pk=scraper_id)

        task_id = self.request.id
        task_instance = celery_app.AsyncResult(task_id)
        result_meta = task_instance._get_task_meta()
        task_name = result_meta.get("task_name")

        print("ATRIBUTOS TASK EXEC GROUP")
        print("TASK_EXEC_GROUP_ID:", self.request.id)
        print("TASK_EXEC_GROUP_INSTANCE_NAME:", task_name)

        scraper_group = ScraperExecutionGroup.objects.create(
            scraper=scraper,
            task_name=task_name,
            status=STATUS_CHOICES[0][0],
        )

        task_scraper_subtasks = [
            task_scraper_subtask.subtask(
                kwargs={
                    "keyword": keyword,
                    "scraper_classname": scraper_classname,
                    "scraper_execution_group_id": scraper_group.id,
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
    """ Adiciona jobs agendados a partir dos scrapers default disponiveis
    """

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
                "scraper_classname": scraper_config["class"],
                "scraper_id": scraper_config["id"],
                "keywords": KEYWORDS,
            }),
            name=scraper.task_name_prefix,
        )
