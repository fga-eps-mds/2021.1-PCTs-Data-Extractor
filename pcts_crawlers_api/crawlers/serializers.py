from rest_framework import serializers
from crawlers.models import Crawler
from crawlers.models import CrawlerExecutionGroup
from crawlers.models import CrawlerExecution

from rest_framework_nested.relations import NestedHyperlinkedRelatedField


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
            'created_at',
            'url',
        ]


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
            'scraped_pages',
            'saved_records',
            'dropped_records',
            'error_log'
        ]


class CrawlerExecutionGroupSerializer(serializers.ModelSerializer):
    crawler_executions = serializers.SerializerMethodField('_get_executions')

    def _get_executions(self, obj):
        serializer = CrawlerExecutionSerializer(obj.crawler_executions.all(), many=True)
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
