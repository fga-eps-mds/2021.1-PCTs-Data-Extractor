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

# from scrapers.models import ScraperExecutionGroup
# from scrapers.models import ScraperExecution


def task_scraper_group_wrapper(task_group_name, task_sub_prefix_name, scraper_id):
    @task(name=task_sub_prefix_name)
    def task_scraper_subtask(keyword, **kwargs):
        run_scraper(scraper_id, keyword)

        # Save ScraperExecutionGroup
        # group = ScraperExecutionGroup.objects.create(
        #     scraper=
        # )

        # scraper = models.ForeignKey(Scraper, on_delete=models.CASCADE)
        # task_name = models.CharField("Task Name", max_length=100)
        # start_datetime = models.DateTimeField("Start Datetime", auto_now_add=True)
        # end_datetime = models.DateTimeField("End Datetime", null=True)
        # status = models.IntegerField(
        #     "Execution Status",
        #     choices=STATUS_CHOICES,
        #     default=1
        # )

        # ScraperExecution.objects.create(
        #     scraper_execution_group=group,

        # )


    # scraped_pages = models.IntegerField()
    # saved_records = models.IntegerField()
    # droped_records = models.IntegerField()
        return True

    @task(name=task_group_name)
    def task_scraper_group(keywords, **kwargs):
        task_scraper_subtasks = [
            task_scraper_subtask.subtask(
                kwargs={"keyword": keyword},
                immutable=True
            )
            for keyword in keywords
        ]
        result = chain(*task_scraper_subtasks).apply_async()
        return True

    return task_scraper_group
