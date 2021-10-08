from rest_framework import serializers
from scrapers.models import Scraper


class ScraperSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Scraper
        fields = [
            'site_name',
            'url_root',
            'next_button_xpath',
            'pagination_retries',
            'pagination_delay',
            'created_at',
        ]
