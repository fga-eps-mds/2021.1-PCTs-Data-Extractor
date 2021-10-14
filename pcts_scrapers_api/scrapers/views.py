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

from scrapers import tasks
from pcts_scrapers_api import celery as celery_tasks

if (os.environ.get("PROJECT_ENV_EXECUTOR", default="HOST") == "DOCKER"):
    sys.path.append('/app/pcts_scraper_jobs')
else:
    sys.path.append('../pcts_scraper_jobs')

from run_scrapers import run_scrapers, run_headless_scraper


class ScraperViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows scrapers to be viewed or edited.
    """
    queryset = Scraper.objects.all().order_by('site_name')
    serializer_class = ScraperSerializer


class ScraperExecutorViewSet(mixins.RetrieveModelMixin,
                             mixins.ListModelMixin,
                             viewsets.GenericViewSet):

    @api_view(['GET'])
    def start(self, *args, **kwargs):
        logger = logging.getLogger(__name__)
        keywords = [
            "povos e comunidades tradicionais",
            "quilombolas",
        ]

        result = run_scrapers(["IncraScraperSpider"], ["quilombolas", "povos e comunidades tradicionais"], headless=False)
        # result = tasks.incra_scraper.delay(keywords=keywords)

        # result = celery_tasks.add.delay(1, 4)
        # result = result.get()

        return Response({
            "message": "Website scraped successfully!",
            "celery": str(result),
        })
