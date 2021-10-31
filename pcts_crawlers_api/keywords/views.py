from rest_framework import viewsets
from keywords.models import Keyword
from keywords.serializers import KeywordSerializer

from crawlers.tasks import sync_periodic_crawlers


class KeywordViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows keywords and key phrases
    to be viewed or edited.
    """
    queryset = Keyword.objects.all().order_by('keyword')
    serializer_class = KeywordSerializer

    def perform_destroy(self, keyword_instance: Keyword):
        super(KeywordViewSet, self).perform_destroy(keyword_instance)
        sync_periodic_crawlers()
