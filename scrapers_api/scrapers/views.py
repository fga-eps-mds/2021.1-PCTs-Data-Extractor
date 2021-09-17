from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from scrapers.serializers import ScraperSerializer

from rest_framework.response import Response

from rest_framework.decorators import api_view
from rest_framework import viewsets
from rest_framework import mixins


class ScraperViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows scrapers to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = ScraperSerializer


class ScraperExecutor(mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):

    @api_view(['GET'])
    def start(self, *args, **kwargs):
        return Response({
            "message": "Hello World"
        })
