import os
import sys
import logging
from django.conf import settings

from scrapers.models import Scraper
from scrapers.models import ScraperExecutionGroup
from rest_framework import viewsets
from rest_framework import permissions
from scrapers.serializers import ScraperSerializer
from scrapers.serializers import ScraperExecutionGroupSerializer

from rest_framework.response import Response

from rest_framework.decorators import api_view
from rest_framework import viewsets
from rest_framework import mixins

from scrapers import tasks

if (os.environ.get("PROJECT_ENV_EXECUTOR", default="HOST") == "DOCKER"):
    sys.path.append('/app/pcts_scraper_jobs')
else:
    sys.path.append('../pcts_scraper_jobs')

from scraper_executor import run_scraper


class ScraperViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows scrapers to be viewed or edited.
    """
    queryset = Scraper.objects.all().order_by('site_name')
    serializer_class = ScraperSerializer


class ScraperExecutionGroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows scraper executions to be viewed.
    """
    queryset = ScraperExecutionGroup.objects.all().order_by('task_name')
    serializer_class = ScraperExecutionGroupSerializer

    # def get_queryset(self):
    #     return ScraperExecutionGroup.objects.filter(scraper=self.kwargs['scraper_pk'])


# class ScraperExecutorViewSet(mixins.RetrieveModelMixin,
#                              mixins.ListModelMixin,
#                              viewsets.GenericViewSet):

#     @api_view(['GET'])
#     def start(self, *args, **kwargs):
#         logger = logging.getLogger(__name__)
#         keywords = [
#             "povos e comunidades tradicionais",
#             "quilombolas",
#         ]

#         result = run_scraper(
#             scraper_id="IncraScraperSpider", keyword="quilombolas")

#         return Response({
#             "message": "Website scraped successfully!",
#             "celery": str(result),
#         })
