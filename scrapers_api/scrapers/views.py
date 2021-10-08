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


sys.path.append('../scrapers')
# from run_scrapers import run_scrapers

sys.path.append('../module_1')
from module1 import show

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

        show()
        # run_scrapers()
        # call_generic_scraper.run_scraper(
        #     settings_file_path="scrapers.scraper_executor.pcts_scrapers.settings",
        #     custom_project_settings={
        #         'SPLASH_URL': 'http://pcts-scrapers-splash:8050',
        #         'SPIDER_MODULES': ['scrapers.scraper_executor.pcts_scrapers.spiders'],
        #         'NEWSPIDER_MODULE': 'scrapers.scraper_executor.pcts_scrapers.spiders',
        #         'SELENIUM_DRIVER_EXECUTABLE_PATH': f"{os.getcwd()}/scrapers/scraper_executor/chromedriver"
        #     },
        #     crawler_process=False,
        #     logging=logger
        # )

        return Response({
            "message": "Website scraped successfully!"
        })
