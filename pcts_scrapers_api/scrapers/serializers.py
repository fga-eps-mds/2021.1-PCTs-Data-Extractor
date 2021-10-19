from rest_framework import serializers
from scrapers.models import Scraper
from scrapers.models import ScraperExecutionGroup
from scrapers.models import ScraperExecution

from rest_framework_nested.relations import NestedHyperlinkedRelatedField


class ScraperSerializer(serializers.HyperlinkedModelSerializer):
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


class ScraperExecutionGroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ScraperExecutionGroup
        fields = [
            'id',
            'scraper',
            'task_name',
            'start_datetime',
            'finish_datetime',
            'status',
        ]


class ScraperExecutionSerializer(serializers.HyperlinkedModelSerializer):
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
            'retrieved_records',
        ]
