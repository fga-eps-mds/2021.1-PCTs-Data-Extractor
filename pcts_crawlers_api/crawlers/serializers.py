import json
from rest_framework import serializers
from crawlers.models import Crawler
from crawlers.models import CrawlerExecutionGroup
from crawlers.models import CrawlerExecution
from keywords.models import Keyword

from crawlers.tasks import create_or_update_periodic_task


class CrawlerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crawler
        fields = [
            'id',
            'site_name',
            'task_name',
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
        keywords = [
            keyword.keyword
            for keyword.ke in Keyword.objects.all()
        ]

        crawler = Crawler.objects.create(
            site_name=validated_data.get("site_name"),
            url_root=validated_data.get("url_root"),
            task_name=validated_data.get(
                "task_name"),
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

        create_or_update_periodic_task(crawler, keywords)

        return crawler

    def update(self, crawler: Crawler, validated_data):
        keywords = [
            keyword.keyword
            for keyword.ke in Keyword.objects.all()
        ]

        crawler.site_name=validated_data.get("site_name")
        crawler.url_root=validated_data.get("url_root")
        crawler.task_name=validated_data.get("task_name")
        crawler.qs_search_keyword_param=validated_data.get("qs_search_keyword_param")
        crawler.contains_end_path_keyword=validated_data.get("contains_end_path_keyword")
        crawler.allowed_domains=validated_data.get("allowed_domains")
        crawler.allowed_paths=validated_data.get("allowed_paths")
        crawler.retries=validated_data.get("retries")
        crawler.page_load_timeout=validated_data.get("page_load_timeout")
        crawler.cron_minute=validated_data.get("cron_minute")
        crawler.cron_hour=validated_data.get("cron_hour")
        crawler.cron_day_of_week=validated_data.get("cron_day_of_week")
        crawler.cron_day_of_month=validated_data.get("cron_day_of_month")
        crawler.cron_month_of_year=validated_data.get("cron_month_of_year")
        crawler.contains_dynamic_js_load=validated_data.get("contains_dynamic_js_load")

        crawler.save()

        create_or_update_periodic_task(crawler, keywords)

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
