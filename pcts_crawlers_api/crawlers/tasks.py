import sys
import os
import json
from datetime import datetime
from celery import Celery
from celery.canvas import chain
from celery import task
from django_celery_beat.models import PeriodicTask
from django_celery_beat.models import PeriodicTasks
from django_celery_beat.models import CrontabSchedule

from pcts_crawlers_api.celery import app as celery_app

from crawlers.models import STARTED
from crawlers.models import SUCCESS
from crawlers.models import FAILURE
from crawlers.models import CrawlerExecution
from crawlers.models import CrawlerExecutionGroup
from crawlers.models import Crawler

from keywords.models import Keyword

ENVIRONMENT_EXEC = os.environ.get("PROJECT_ENV_EXECUTOR", default="HOST")
if ENVIRONMENT_EXEC == "DOCKER":
    sys.path.append('/app/pcts_crawlers_scripts')
elif ENVIRONMENT_EXEC == "TEST":
    sys.path.append('pcts_crawlers_scripts')
else:
    sys.path.append('../pcts_crawlers_scripts')
from crawler_executor import run_generic_crawler


TASK_CRAWLER_GROUP_FINISH_NAME = "crawler_finish"
TASK_CRAWLER_KEYWORD_NAME = "crawler_keyword"
TASK_CRAWLER_GROUP_START_NAME = "crawler_group_start"


@task(name=TASK_CRAWLER_GROUP_FINISH_NAME, bind=True)
def task_crawler_group_finish(self, subtasks_result, crawler_execution_group_id):
    crawler_execution_group = CrawlerExecutionGroup.objects.get(
        pk=crawler_execution_group_id
    )

    crawler_execution_group.state = \
        SUCCESS if subtasks_result else FAILURE
    crawler_execution_group.finish_datetime = datetime.now()
    crawler_execution_group.save()

    return subtasks_result


@task(name=TASK_CRAWLER_KEYWORD_NAME, bind=True, time_limit=sys.maxsize)
def task_crawler_keyword(self, prev_subtasks,
                         crawler_execution_group_id, crawler_args,
                         keyword, **kwargs):
    print("INICIANDO CRAWLER KEYWORD")

    crawler_execution_group = CrawlerExecutionGroup.objects.get(
        pk=crawler_execution_group_id
    )

    task_id = self.request.id
    task_instance = celery_app.AsyncResult(task_id)
    result_meta = task_instance._get_task_meta()
    task_name = result_meta.get("task_name")

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


@task(name=TASK_CRAWLER_GROUP_START_NAME, bind=True)
def task_crawler_group(self, crawler_id, crawler_args,
                       keywords, **kwargs):
    try:
        print("INICIANDO CRAWLER GROUP")
        crawler = Crawler.objects.get(pk=crawler_id)

        task_id = self.request.id
        task_instance = celery_app.AsyncResult(task_id)
        result_meta = task_instance._get_task_meta()
        task_name = result_meta.get("task_name")

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
                task_crawler_keyword.subtask(
                    kwargs=task_args
                )
            )

        task_finish_group_exec_subtask = \
            task_crawler_group_finish.subtask(
                kwargs={
                    "crawler_execution_group_id": crawler_group.id,
                },
            )

        chain(
            *task_crawler_subtasks,
            task_finish_group_exec_subtask
        ).apply_async()
    except Exception as e:
        print("EXCECAO:", str(e))
        raise e

    return True


def get_periodic_task(task_name):
    try:
        return PeriodicTask.objects.get(name=task_name)
    except Exception:
        return None


def get_crontab_scheduler(minute, hour, day_of_week, day_of_month, month_of_year):
    crontab_args = {
        "minute": minute,
        "hour": hour,
        "day_of_week": day_of_week,
        "day_of_month": day_of_month,
        "month_of_year": month_of_year
    }

    try:
        crontab_scheduler = CrontabSchedule.objects.get(**crontab_args)
    except Exception:
        crontab_scheduler = CrontabSchedule.objects.create(**crontab_args)
    return crontab_scheduler


def create_crawler_periodic_task(crawler: Crawler, keywords=[]):
    task = PeriodicTask.objects.create(
        name=crawler.task_name,
        task=TASK_CRAWLER_GROUP_START_NAME,
        crontab=get_crontab_scheduler(
            crawler.cron_minute,
            crawler.cron_hour,
            crawler.cron_day_of_week,
            crawler.cron_day_of_month,
            crawler.cron_month_of_year
        ),
        enabled=crawler.task_enabled,
        one_off=crawler.task_one_off,
        kwargs=json.dumps({
            "crawler_id": crawler.id,
            "crawler_args": {
                "site_name": crawler.site_name,
                "task_name": crawler.task_name,
                "url_root": crawler.url_root,
                "qs_search_keyword_param": crawler.qs_search_keyword_param,
                "contains_end_path_keyword": crawler.contains_end_path_keyword,
                "allowed_domains": crawler.allowed_domains,
                "allowed_paths": crawler.allowed_paths,
                "retries": crawler.retries,
                "page_load_timeout": crawler.page_load_timeout,
                "contains_dynamic_js_load": crawler.contains_dynamic_js_load,
            },
            "keywords": keywords,
        })
    )

    PeriodicTasks.changed(task)


def update_periodic_task(task: PeriodicTask, crawler: Crawler,
                         keywords=[]):
    task.enabled = crawler.task_enabled
    task.one_off = crawler.task_one_off
    task.kwargs = json.dumps({
        "crawler_id": crawler.id,
        "crawler_args": {
            "site_name": crawler.site_name,
            "task_name": crawler.task_name,
            "url_root": crawler.url_root,
            "qs_search_keyword_param": crawler.qs_search_keyword_param,
            "contains_end_path_keyword": crawler.contains_end_path_keyword,
            "allowed_domains": crawler.allowed_domains,
            "allowed_paths": crawler.allowed_paths,
            "retries": crawler.retries,
            "page_load_timeout": crawler.page_load_timeout,
            "contains_dynamic_js_load": crawler.contains_dynamic_js_load,
        },
        "keywords": keywords,
    })
    task.crontab = get_crontab_scheduler(
        crawler.cron_minute,
        crawler.cron_hour,
        crawler.cron_day_of_week,
        crawler.cron_day_of_month,
        crawler.cron_month_of_year
    )
    task.interval = None
    task.solar = None
    task.clocked = None
    task.save()


def create_or_update_periodic_task(crawler: Crawler, keywords=[]):
    taskname = crawler.task_name
    task = get_periodic_task(taskname)
    if task:
        print("ATUALIZANDO TASK:", taskname)
        update_periodic_task(
            task,
            crawler,
            keywords
        )
    else:
        print("ADICIONANDO TASK:", taskname)
        create_crawler_periodic_task(
            crawler,
            keywords
        )


def delete_crawler_periodic_task(crawler: Crawler):
    task = PeriodicTask.objects.get(name=crawler.task_name)
    task.delete()


def truncate_crawler_celery_periodic_tasks():
    PeriodicTask.objects.filter(
        task=TASK_CRAWLER_GROUP_START_NAME
    ).delete()


def sync_periodic_crawlers():
    """ Adiciona jobs agendados a partir dos crawler default disponiveis
    """

    try:
        keywords = [
            keyword.keyword
            for keyword in Keyword.objects.all()
        ]
    except Exception:
        keywords = []

    print("SINCRONIZANDO PERIODIC TASKS")

    crawlers = Crawler.objects.all()
    truncate_crawler_celery_periodic_tasks()
    for crawler in crawlers:
        print("SINCRONIZAR TASK:", crawler.task_name)
        try:
            create_or_update_periodic_task(crawler, keywords)
        except Exception as e:
            print("EXCECAO AO SINCRONIZAR TASK:", str(e))
            raise e

# ============================= AUTO CREATE SCHEDULERS ON STARTUP


@celery_app.on_after_finalize.connect
def sync_periodic_crawlers_startup(sender: Celery, **kwargs):
    """ Setup periodic tasks on start up
    """
    sync_periodic_crawlers()
