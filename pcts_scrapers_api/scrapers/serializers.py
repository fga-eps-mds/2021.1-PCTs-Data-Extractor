from rest_framework import serializers
from scrapers.models import Scraper
from scrapers.models import ScraperExecutionGroup
from scrapers.models import ScraperExecution


class ScraperSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Scraper
        fields = [
            'site_name',
            'url_root',
            'task_name_prefix',
            'created_at',
        ]


class ScraperExecutionGroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ScraperExecutionGroup
        fields = [
            'scraper',
            'task_name',
            'start_datetime',
            'end_datetime',
            'status',
        ]


class ScraperExecutionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ScraperExecution
        fields = [
            'scraper_execution_group',
            'task_id',
            'task_name',
            'start_datetime',
            'end_datetime',
            'keyword',
            'status',
            'retrieved_records',
        ]
