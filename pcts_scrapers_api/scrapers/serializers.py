from rest_framework import serializers
from scrapers.models import Scraper
from scrapers.models import ScraperExecutionGroup
from scrapers.models import ScraperExecution

from rest_framework_nested.relations import NestedHyperlinkedRelatedField


class ScraperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scraper
        fields = [
            'id',
            'site_name',
            'url_root',
            'task_name_prefix',
            'created_at',
            'url',
        ]


class ScraperExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScraperExecution
        fields = [
            'id',
            'scraper_execution_group',
            'task_id',
            'task_name',
            'start_datetime',
            'finish_datetime',
            'keyword',
            'status',
            'scraped_pages',
            'saved_records',
            'dropped_records',
            'error_log'
        ]


class ScraperExecutionGroupSerializer(serializers.ModelSerializer):
    scraper_executions = serializers.SerializerMethodField('_get_executions')

    def _get_executions(self, obj):
        serializer = ScraperExecutionSerializer(obj.scraper_executions_keywords.all(), many=True)
        return serializer.data

    class Meta:
        model = ScraperExecutionGroup
        fields = [
            'id',
            'scraper',
            'task_name',
            'start_datetime',
            'finish_datetime',
            'status',
            'scraper_executions'
        ]
