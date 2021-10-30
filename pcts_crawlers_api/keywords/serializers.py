from keywords.models import Keyword
from rest_framework import serializers


class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = [
            'id',
            'keyword',
            'created_at',
            'url'
        ]
