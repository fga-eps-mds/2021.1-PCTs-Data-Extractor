from rest_framework import viewsets
from keywords.models import Keyword
from keywords.serializers import KeywordSerializer


class KeywordViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows keywords and key phrases
    to be viewed or edited.
    """
    queryset = Keyword.objects.all().order_by('keyword')
    serializer_class = KeywordSerializer
