from keywords.models import Keyword
from rest_framework import serializers

from crawlers.tasks import sync_periodic_crawlers


class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = [
            'id',
            'keyword',
            'created_at',
            'url'
        ]

    def create(self, validated_data):
        keyword = super(KeywordSerializer, self).create(validated_data)
        sync_periodic_crawlers()
        return keyword

    def update(self, keyword: Keyword, validated_data):
        keyword = super(KeywordSerializer, self).update(keyword, validated_data)
        sync_periodic_crawlers()
        return keyword
