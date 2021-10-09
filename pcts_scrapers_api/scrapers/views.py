import os
import sys
import logging
from django.conf import settings

from .models import Scraper
from rest_framework import viewsets
from rest_framework import permissions
from scrapers.serializers import ScraperSerializer

from rest_framework.response import Response

from rest_framework.decorators import api_view
from rest_framework import viewsets
from rest_framework import mixins

from scrapers.tasks import add

sys.path.append('../pcts_scraper_jobs')
from run_scrapers import run_scrapers


class ScraperViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows scrapers to be viewed or edited.
    """
    queryset = Scraper.objects.all().order_by('site_name')
    serializer_class = ScraperSerializer


class ScraperExecutor(mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):

    @api_view(['GET'])
    def start(self, *args, **kwargs):
        logger = logging.getLogger(__name__)

        # run_scrapers(choosen_scrapers=["IncraScraperSpider"])

        result = add.delay(1, 4)
        result = result.get(timeout=5)

        return Response({
            "message": "Website scraped successfully!",
            "celery": str(result),
        })
