import os
import logging
from django.conf import settings

from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from scrapers.serializers import ScraperSerializer

from rest_framework.response import Response

from rest_framework.decorators import api_view
from rest_framework import viewsets
from rest_framework import mixins


from .utils import call_generic_scraper
import importlib.machinery

# call_generic_scraper = importlib.machinery.SourceFileLoader('modulename','/app/scrapers/call_generic_scraper.py').load_module()
# call_generic_scraper = importlib.machinery.SourceFileLoader('modulename','/app/scrapers/call_generic_scraper.py').load_module()

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
        logger = logging.getLogger(__name__)

        logger.info("COM LOGGER")
        call_generic_scraper.run_scraper(
            settings_file_path="scrapers.utils.pcts_scrapers.settings",
            custom_project_settings={
                'SPLASH_URL': 'http://pcts-scrapers-splash:8050',
                'SPIDER_MODULES': ['scrapers.utils.pcts_scrapers.spiders'],
                'NEWSPIDER_MODULE': 'scrapers.utils.pcts_scrapers.spiders',
                'SELENIUM_DRIVER_EXECUTABLE_PATH': f"{os.getcwd()}/scrapers/utils/chromedriver"
            },
            crawler_process=False,
            logging=logger
        )

        return Response({
            "message": "Website scraped successfully!"
        })
