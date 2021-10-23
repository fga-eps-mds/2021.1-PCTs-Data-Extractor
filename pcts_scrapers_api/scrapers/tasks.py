from scrapers.models import STATUS_STARTED, STATUS_SUCCESS, STATUS_FAILED
from scrapers.models import ScraperExecution
from scrapers.models import ScraperExecutionGroup
from scrapers.models import Scraper
import sys
import os

from datetime import datetime
from celery import Celery
from celery.app import task as task_obj
from celery import shared_task, task
from celery.schedules import crontab
from celery.canvas import group, chain, chord
from pcts_scrapers_api.celery import app as celery_app

ENVIRONMENT_EXEC = os.environ.get("PROJECT_ENV_EXECUTOR", default="HOST")
if ENVIRONMENT_EXEC == "DOCKER":
    sys.path.append('/app/pcts_scraper_jobs')
elif ENVIRONMENT_EXEC == "TEST":
    sys.path.append('pcts_scraper_jobs')
else:
    sys.path.append('../pcts_scraper_jobs')
from scraper_executor import run_scraper, run_generic_scraper


def task_scraper_group_wrapper(task_group_name, task_sub_prefix_name):
    """ Wrapper do task group de execucao de um scraper inteiro
        e a subtask de execucao de uma keyword por vez
    """

    @task(name=f"{task_group_name}_finish", bind=True)
    def task_finish_group_execution(self, prev_task_result, scraper_execution_group_id):
        scraper_execution_group = ScraperExecutionGroup.objects.get(
            pk=scraper_execution_group_id
        )

        scraper_execution_group.status = \
            STATUS_SUCCESS if prev_task_result else STATUS_FAILED
        scraper_execution_group.finish_datetime = datetime.now()
        scraper_execution_group.save()

        return prev_task_result

    @task(name=task_sub_prefix_name, bind=True)
    def task_scraper_subtask(self, prev_task_result,
                             scraper_execution_group_id, scraper_args,
                             keyword, **kwargs):
        scraper_execution_group = ScraperExecutionGroup.objects.get(
            pk=scraper_execution_group_id
        )

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
            status=STATUS_STARTED
        )

        result_status = True
        try:
            execution_stats = run_generic_scraper(
                scraper_args=scraper_args,
                keyword=keyword
            )

            # Update execution monitoring on success
            scraper_execution.finish_datetime = datetime.now()
            scraper_execution.status = STATUS_SUCCESS
            scraper_execution.scraped_pages = execution_stats.get(
                "downloader/request_count") or 0
            scraper_execution.saved_records = execution_stats.get(
                "saved_records") or 0
            scraper_execution.dropped_records = execution_stats.get(
                "droped_records") or 0
        except Exception as e:
            # Update execution monitoring on fail

            scraper_execution.error_log = str(e)
            scraper_execution.finish_datetime = datetime.now()
            scraper_execution.status = STATUS_FAILED

            result_status = False

        scraper_execution.save()

        if prev_task_result == None:
            return result_status
        else:
            return prev_task_result and result_status

    @task(name=f"{task_group_name}_start", bind=True)
    def task_scraper_group(self, scraper_id, scraper_args, keywords, **kwargs):
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
            status=STATUS_STARTED,
        )

        task_scraper_subtasks = []
        for idx, keyword in enumerate(keywords):
            task_args = {
                "scraper_execution_group_id": scraper_group.id,
                "scraper_args": scraper_args,
                "keyword": keyword,
            }

            # A primeira task da chain, possui o argumento a prev_task_result.
            # Nas próximas tasks, o próprio Celery irá setar
            # este atributo com o resultado da task anterior
            if idx == 0:
                task_args["prev_task_result"] = None

            task_scraper_subtasks.append(
                task_scraper_subtask.subtask(
                    kwargs=task_args,
                    # immutable=True
                )
            )

        task_finish_group_exec_subtask = task_finish_group_execution.subtask(
            kwargs={
                "scraper_execution_group_id": scraper_group.id
            },
        )

        result = chain(
            *task_scraper_subtasks,
            task_finish_group_exec_subtask
        ).apply_async()

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

    scrapers = Scraper.objects.all()
    for scraper in scrapers:
        sender.add_periodic_task(
            crontab(minute='0', hour='4', day_of_week='*',
                    day_of_month='*', month_of_year='*'),
            task_scraper_group_wrapper(
                scraper.task_name_prefix,
                f"{scraper.task_name_prefix}_keyword",
            ).subtask(kwargs={
                "scraper_id": scraper.id,
                "scraper_args": {
                    "site_name": scraper.site_name,
                    "url_root": scraper.url_root,
                    "task_name_prefix": scraper.task_name_prefix,
                    "js_search_steps": scraper.js_search_steps,
                    "next_button_xpath": scraper.next_button_xpath,
                    "allowed_domains": scraper.allowed_domains,
                    "allowed_paths": scraper.allowed_paths,
                    "restrict_xpaths": scraper.restrict_xpaths,
                    "restrict_css": scraper.restrict_css,
                    "content_xpath": scraper.content_xpath,
                    "query_string_params": scraper.query_string_params,
                    "pagination_retries": scraper.pagination_retries,
                    "pagination_delay": scraper.pagination_delay,
                    "page_load_timeout": scraper.page_load_timeout
                },
                "keywords": KEYWORDS,
            }),
            name=scraper.task_name_prefix,
        )
