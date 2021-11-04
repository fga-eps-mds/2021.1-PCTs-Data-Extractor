import os
import sys
import logging
from django.conf import settings

from crawlers.models import Crawler
from crawlers.models import CrawlerExecutionGroup
from rest_framework import viewsets
from rest_framework import permissions
from crawlers.serializers import CrawlerSerializer
from crawlers.serializers import CrawlerExecutionGroupSerializer
from multiprocessing import Process

from rest_framework.request import Request
from rest_framework.response import Response

from rest_framework.decorators import api_view
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import generics

from pcts_crawlers_api import celery as root_tasks
from crawlers import tasks

from crawlers.tasks import delete_crawler_periodic_task

ENVIRONMENT_EXEC = os.environ.get("PROJECT_ENV_EXECUTOR", default="HOST")
if ENVIRONMENT_EXEC == "DOCKER":
    sys.path.append('/app/pcts_crawlers_scripts')
elif ENVIRONMENT_EXEC == "TEST":
    sys.path.append('pcts_crawlers_scripts')
else:
    sys.path.append('../pcts_crawlers_scripts')
from crawler_executor import run_generic_crawler


class CrawlerViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows crawlers to be viewed or edited.
    """
    queryset = Crawler.objects.all().order_by('site_name')
    serializer_class = CrawlerSerializer

    def perform_destroy(self, crawler_instance: Crawler):
        delete_crawler_periodic_task(crawler_instance)
        super(CrawlerViewSet, self).perform_destroy(crawler_instance)


class CrawlerExecutionGroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows crawler executions to be viewed.
    """
    serializer_class = CrawlerExecutionGroupSerializer

    def get_queryset(self):
        queryset = CrawlerExecutionGroup.objects.\
            filter(crawler=self.kwargs['crawler_pk'])
        order_by = self.request.GET.get('order-by', '-finish_datetime')

        return queryset.order_by(order_by)


class CrawlerExecutorViewSet(generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        keyword = request.query_params.get('keyword')

        # result = None
        # if not keyword:
        #     result = "É necessário informar uma expressão chave (parametro keyword)"
        # else:
        #     process = Process(
        #         target=run_generic_crawler,
        #         kwargs=dict(
        #             keyword=keyword,
        #         )
        #     )
        #     process.start()
        #     process.join()
        #     result = "Site 'raspado' com sucesso"

        # return Response({
        #     "message": str(result),
        # })
