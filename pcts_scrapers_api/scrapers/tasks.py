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


def task_scraper_group_wrapper(task_group_name, task_sub_prefix_name, scraper_id):
    @shared_task(name=task_sub_prefix_name)
    def task_scraper_subtask(keyword, **kwargs):
        run_scraper(scraper_id, keyword)
        return True

    @shared_task(name=task_group_name)
    def task_scraper_group(keywords, **kwargs):
        task_scraper_subtasks = [
            task_scraper_subtask.subtask(
                kwargs={"keyword": keyword}, immutable=True)
            for keyword in keywords
        ]
        result = chain(*task_scraper_subtasks).apply_async()
        return True

    return task_scraper_group
