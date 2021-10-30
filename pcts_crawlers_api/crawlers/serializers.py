import json
from rest_framework import serializers
from crawlers.models import Crawler
from crawlers.models import CrawlerExecutionGroup
from crawlers.models import CrawlerExecution

from rest_framework_nested.relations import NestedHyperlinkedRelatedField

from pcts_crawlers_api.celery import app as celery_app
from crawlers.tasks import create_periodic_task


class CrawlerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crawler
        fields = [
            'id',
            'site_name',
            'task_name_prefix',
            'url_root',
            'qs_search_keyword_param',
            'contains_end_path_keyword',
            'allowed_domains',
            'allowed_paths',
            'retries',
            'page_load_timeout',
            'cron_minute',
            'cron_hour',
            'cron_day_of_week',
            'cron_day_of_month',
            'cron_month_of_year',
            'contains_dynamic_js_load',
            'created_at',
            'url',
        ]

    def create(self, validated_data):
        KEYWORDS = [
            "povos e comunidades tradicionais",
            "quilombolas",
        ]

        crawler = Crawler.objects.create(
            site_name=validated_data.get("site_name"),
            url_root=validated_data.get("url_root"),
            task_name_prefix=validated_data.get(
                "task_name_prefix"),
            qs_search_keyword_param=validated_data.get(
                "qs_search_keyword_param"),
            contains_end_path_keyword=validated_data.get(
                "contains_end_path_keyword"),
            allowed_domains=validated_data.get(
                "allowed_domains"),
            allowed_paths=validated_data.get(
                "allowed_paths"),
            retries=validated_data.get("retries"),
            page_load_timeout=validated_data.get(
                "page_load_timeout"),
            cron_minute=validated_data.get("cron_minute"),
            cron_hour=validated_data.get("cron_hour"),
            cron_day_of_week=validated_data.get("cron_day_of_week"),
            cron_day_of_month=validated_data.get("cron_day_of_month"),
            cron_month_of_year=validated_data.get("cron_month_of_year"),
            contains_dynamic_js_load=validated_data.get(
                "contains_dynamic_js_load"),
        )

        create_periodic_task(celery_app, crawler, KEYWORDS)

        from django_celery_beat.models import PeriodicTask, PeriodicTasks, CrontabSchedule


        # crontab = CrontabSchedule.objects.create(
        #     minute=crawler.cron_minute,
        #     hour=crawler.cron_hour,
        #     day_of_week=crawler.cron_day_of_week,
        #     day_of_month=crawler.cron_day_of_month,
        #     month_of_year=crawler.cron_month_of_year
        # )

        # all_crawler_args = {
        #     "crawler_id": crawler.id,
        #     "crawler_args": {
        #         "site_name": crawler.site_name,
        #         "url_root": crawler.url_root,
        #         "qs_search_keyword_param": crawler.qs_search_keyword_param,
        #         "contains_end_path_keyword": crawler.contains_end_path_keyword,
        #         "task_name_prefix": crawler.task_name_prefix,
        #         "allowed_domains": crawler.allowed_domains,
        #         "allowed_paths": crawler.allowed_paths,
        #         "retries": crawler.retries,
        #         "page_load_timeout": crawler.page_load_timeout,
        #         "contains_dynamic_js_load": crawler.contains_dynamic_js_load,
        #     },
        #     "keywords": KEYWORDS,
        # }

        # PeriodicTask.objects.create(
        #     name=f"{crawler.task_name_prefix}_start",
        #     task=f"{crawler.task_name_prefix}_start",
        #     crontab=crontab,
        # )


        return crawler


class CrawlerExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrawlerExecution
        fields = [
            'id',
            'crawler_execution_group',
            'task_id',
            'task_name',
            'start_datetime',
            'finish_datetime',
            'keyword',
            'state',
            'crawled_pages',
            'saved_records',
            'dropped_records',
            'error_log'
        ]


class CrawlerExecutionGroupSerializer(serializers.ModelSerializer):
    crawler_executions = serializers.SerializerMethodField('_get_executions')

    def _get_executions(self, obj):
        serializer = CrawlerExecutionSerializer(
            obj.crawler_executions.all(), many=True)
        return serializer.data

    class Meta:
        model = CrawlerExecutionGroup
        fields = [
            'id',
            'crawler',
            'task_name',
            'start_datetime',
            'finish_datetime',
            'state',
            'crawler_executions'
        ]
