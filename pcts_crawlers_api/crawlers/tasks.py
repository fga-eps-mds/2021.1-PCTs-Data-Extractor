import sys
import os
from datetime import datetime
from celery import Celery
from celery.app import task as task_obj
from crawlers.models import CrawlerExecutionGroup
from crawlers.models import Crawler
from celery.canvas import group, chain, chord
from celery.schedules import crontab
from celery import shared_task, task

from pcts_crawlers_api.celery import app as celery_app

from crawlers.models import STARTED
from crawlers.models import SUCCESS
from crawlers.models import FAILURE
from crawlers.models import CrawlerExecution

from keywords.models import Keyword


ENVIRONMENT_EXEC = os.environ.get("PROJECT_ENV_EXECUTOR", default="HOST")
if ENVIRONMENT_EXEC == "DOCKER":
    sys.path.append('/app/pcts_crawlers_scripts')
elif ENVIRONMENT_EXEC == "TEST":
    sys.path.append('pcts_crawlers_scripts')
else:
    sys.path.append('../pcts_crawlers_scripts')
from crawler_executor import run_generic_crawler


def task_crawler_group_wrapper(task_group_name, task_sub_prefix_name):
    """ Wrapper do task group de execucao de um crawler inteiro
        e a subtask de execucao de uma keyword por vez
    """

    @task(name=f"{task_group_name}_finish", bind=True)
    def task_finish_group_execution(self, subtasks_result, crawler_execution_group_id):
        crawler_execution_group = CrawlerExecutionGroup.objects.get(
            pk=crawler_execution_group_id
        )

        crawler_execution_group.state = \
            SUCCESS if subtasks_result else FAILURE
        crawler_execution_group.finish_datetime = datetime.now()
        crawler_execution_group.save()

        return subtasks_result

    @task(name=task_sub_prefix_name, bind=True, time_limit=sys.maxsize)
    def task_crawler_subtask(self, prev_subtasks,
                             crawler_execution_group_id, crawler_args,
                             keyword, **kwargs):
        crawler_execution_group = CrawlerExecutionGroup.objects.get(
            pk=crawler_execution_group_id
        )

        task_id = self.request.id
        task_instance = celery_app.AsyncResult(task_id)
        result_meta = task_instance._get_task_meta()
        task_name = result_meta.get("task_name")

        print("ATRIBUTOS TASK EXEC")
        print("TASK_EXEC_ID:", self.request.id)
        print("TASK_EXEC_INSTANCE_NAME:", task_name)

        # Start execution monitoring
        crawler_execution = CrawlerExecution.objects.create(
            crawler_execution_group=crawler_execution_group,
            task_id=task_id,
            task_name=task_name,
            keyword=keyword,
            state=STARTED
        )

        result_state = True

        try:
            execution_stats = run_generic_crawler(
                crawler_args=crawler_args,
                keyword=keyword
            )

            # Update execution monitoring on success
            crawler_execution.crawled_pages = execution_stats.get(
                "downloader/request_count") or 0
            crawler_execution.saved_records = execution_stats.get(
                "saved_records") or 0
            crawler_execution.dropped_records = execution_stats.get(
                "droped_records") or 0
            crawler_execution.state = SUCCESS
        except Exception as e:
            result_state = False
            crawler_execution.state = FAILURE
            crawler_execution.error_log = str(e)
        finally:
            crawler_execution.finish_datetime = datetime.now()
            crawler_execution.save()

        if prev_subtasks == None:
            return result_state
        else:
            return prev_subtasks and result_state

    @task(name=f"{task_group_name}_start", bind=True)
    def task_crawler_group(self, crawler_id, crawler_args, keywords=[], **kwargs):
        crawler = Crawler.objects.get(pk=crawler_id)

        task_id = self.request.id
        task_instance = celery_app.AsyncResult(task_id)
        result_meta = task_instance._get_task_meta()
        task_name = result_meta.get("task_name")

        print("ATRIBUTOS TASK EXEC GROUP")
        print("TASK_EXEC_GROUP_ID:", self.request.id)
        print("TASK_EXEC_GROUP_INSTANCE_NAME:", task_name)

        crawler_group = CrawlerExecutionGroup.objects.create(
            crawler=crawler,
            task_name=task_name,
            state=STARTED,
        )

        task_crawler_subtasks = []
        if not keywords:
            keywords.append("")

        for idx, keyword in enumerate(keywords):
            task_args = {
                "crawler_execution_group_id": crawler_group.id,
                "crawler_args": crawler_args,
                "keyword": keyword,
            }

            # A primeira task da chain, possui o argumento a prev_subtasks.
            # Nas próximas tasks, o próprio Celery irá setar
            # este atributo com o resultado da task anterior
            if idx == 0:
                task_args["prev_subtasks"] = None

            task_crawler_subtasks.append(
                task_crawler_subtask.subtask(
                    kwargs=task_args
                )
            )

        task_finish_group_exec_subtask = task_finish_group_execution.subtask(
            kwargs={
                "crawler_execution_group_id": crawler_group.id
            },
        )

        chain(
            *task_crawler_subtasks,
            task_finish_group_exec_subtask
        ).apply_async()

        return True

    return task_crawler_group


def create_periodic_task(sender: Celery, crawler: Crawler, keywords=[]):
    sender.add_periodic_task(
        crontab(
            minute=crawler.cron_minute,
            hour=crawler.cron_hour,
            day_of_week=crawler.cron_day_of_week,
            day_of_month=crawler.cron_day_of_month,
            month_of_year=crawler.cron_month_of_year
        ),
        task_crawler_group_wrapper(
            crawler.task_name_prefix,
            f"{crawler.task_name_prefix}_keyword",
        ).subtask(kwargs={
            "crawler_id": crawler.id,
            "crawler_args": {
                "site_name": crawler.site_name,
                "url_root": crawler.url_root,
                "qs_search_keyword_param": crawler.qs_search_keyword_param,
                "contains_end_path_keyword": crawler.contains_end_path_keyword,
                "task_name_prefix": crawler.task_name_prefix,
                "allowed_domains": crawler.allowed_domains,
                "allowed_paths": crawler.allowed_paths,
                "retries": crawler.retries,
                "page_load_timeout": crawler.page_load_timeout,
                "contains_dynamic_js_load": crawler.contains_dynamic_js_load,
            },
            "keywords": keywords,
        }),
        name=crawler.task_name_prefix,
    )


# ============================= AUTO CREATE SCHEDULERS ON STARTUP
@celery_app.on_after_finalize.connect
def setup_periodic_crawlers(sender: Celery, **kwargs):
    """ Adiciona jobs agendados a partir dos crawler default disponiveis
    """

    try:
        keywords = [
            keyword.keyword
            for keyword in Keyword.objects.all()
        ]
    except Exception:
        keywords = []

    print("ADICIONANDO PERIODIC TASKS")

    crawler = Crawler.objects.all()
    for crawler in crawler:
        create_periodic_task(sender, crawler, keywords)
