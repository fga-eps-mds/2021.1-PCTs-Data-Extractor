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
            'site_name_display',
            'task_name',
            'task_enabled',
            'task_one_off',
            'url_root',
            'qs_search_keyword_param',
            'contains_end_path_keyword',
            'allowed_domains',
            'allowed_paths',
            'page_load_timeout',
            'cron_minute',
            'cron_hour',
            'cron_day_of_week',
            'cron_day_of_month',
            'cron_month_of_year',
            'created_at',
            'url',
        ]

    def create(self, validated_data):
        keywords = [
            keyword.keyword
            for keyword in Keyword.objects.all()
        ]
        

        crawler = Crawler.objects.create(
            site_name=validated_data.get("site_name"),
            site_name_display=validated_data.get("site_name_display"),
            url_root=validated_data.get("url_root"),
            task_name=validated_data.get(
                "task_name"),
            task_enabled=validated_data.get(
                "task_enabled"),
            task_one_off=validated_data.get(
                "task_one_off"),
            qs_search_keyword_param=validated_data.get(
                "qs_search_keyword_param"),
            contains_end_path_keyword=validated_data.get(
                "contains_end_path_keyword"),
            allowed_domains=validated_data.get(
                "allowed_domains"),
            allowed_paths=validated_data.get(
                "allowed_paths"),
            page_load_timeout=validated_data.get(
                "page_load_timeout"),
            cron_minute=validated_data.get("cron_minute") or '0',
            cron_hour=validated_data.get("cron_hour") or '4',
            cron_day_of_week=validated_data.get("cron_day_of_week") or '*',
            cron_day_of_month=validated_data.get("cron_day_of_month") or '*',
            cron_month_of_year=validated_data.get("cron_month_of_year") or '*',
        )

        create_or_update_periodic_task(crawler, keywords)

        return crawler

    def update(self, crawler: Crawler, validated_data):
        keywords = [
            keyword.keyword
            for keyword in Keyword.objects.all()
        ]

        crawler.site_name=validated_data.get("site_name")
        crawler.site_name_display=validated_data.get("site_name_display")
        crawler.url_root=validated_data.get("url_root")
        crawler.task_name=validated_data.get("task_name")
        crawler.task_enabled=validated_data.get("task_enabled")
        crawler.task_one_off=validated_data.get("task_one_off")
        crawler.qs_search_keyword_param=validated_data.get("qs_search_keyword_param")
        crawler.contains_end_path_keyword=validated_data.get("contains_end_path_keyword")
        crawler.allowed_domains=validated_data.get("allowed_domains")
        crawler.allowed_paths=validated_data.get("allowed_paths")
        crawler.page_load_timeout=validated_data.get("page_load_timeout")
        crawler.cron_minute=validated_data.get("cron_minute") or '0'
        crawler.cron_hour=validated_data.get("cron_hour") or '4'
        crawler.cron_day_of_week=validated_data.get("cron_day_of_week") or '*'
        crawler.cron_day_of_month=validated_data.get("cron_day_of_month") or '*'
        crawler.cron_month_of_year=validated_data.get("cron_month_of_year") or '*'

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
