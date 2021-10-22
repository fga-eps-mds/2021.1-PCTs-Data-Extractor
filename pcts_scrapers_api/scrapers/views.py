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
from multiprocessing import Process

from rest_framework.response import Response

from rest_framework.decorators import api_view
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import generics

from pcts_scrapers_api import celery as root_tasks
from scrapers import tasks

ENVIRONMENT_EXEC = os.environ.get("PROJECT_ENV_EXECUTOR", default="HOST")
if ENVIRONMENT_EXEC == "DOCKER":
    sys.path.append('/app/pcts_scraper_jobs')
elif ENVIRONMENT_EXEC == "TEST":
    sys.path.append('pcts_scraper_jobs')
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
    serializer_class = ScraperExecutionGroupSerializer

    def get_queryset(self):
        return ScraperExecutionGroup.objects.\
            filter(scraper=self.kwargs['scraper_pk']).\
            order_by('task_name')


class ScraperExecutorViewSet(generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        logger = logging.getLogger(__name__)
        keyword = request.query_params.get('keyword')

        result = None
        if not keyword:
            result = "É necessário informar uma expressão chave (parametro keyword)"
        else:
            process = Process(
                target=run_scraper,
                kwargs=dict(
                    scraper_id="MpfScraperSpider",
                    keyword=keyword,
                )
            )
            process.start()
            process.join()
            result = "Site 'raspado' com sucesso"

        return Response({
            "message": str(result),
        })
