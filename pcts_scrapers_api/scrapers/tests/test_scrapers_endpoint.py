from rest_framework.test import APITestCase
from django.urls import reverse
from datetime import datetime
import json

from scrapers.models import Scraper
from scrapers.models import ScraperExecution
from scrapers.models import ScraperExecutionGroup
from scrapers.models import STATUS_STARTED


class TestScraperEndpoint(APITestCase):

    def setUp(self):
        self.endpoint = '/api/scrapers/'

    def tearDown(self):
        Scraper.objects.all().delete()

    def test_list_all_scrapers(self):
        Scraper.objects.bulk_create([
            Scraper(site_name="mpf", url_root="www.mpf.mp.br",
                    task_name_prefix="mpf_scraper"),
            Scraper(site_name="incra", url_root="www.gov.br/incra/pt-br",
                    task_name_prefix="incra_scraper"),
            Scraper(site_name="tcu", url_root="pesquisa.apps.tcu.gov.br",
                    task_name_prefix="tcu_scraper"),
        ])

        response = json.loads(self.client.get(
            self.endpoint,
            format='json'
        ).content)

        self.assertEqual(
            3,
            len(response['results']),
        )


class TestScraperExecutionsEndpoint(APITestCase):

    def setUp(self):
        self.endpoint_base = '/api/scrapers'

    def tearDown(self):
        Scraper.objects.all().delete()

    def test_list_all_scraper_executions(self):
        scraper = Scraper.objects.create(
            site_name="mpf",
            url_root="www.mpf.mp.br",
            task_name_prefix="mpf_scraper"
        )

        scraper_group_exec = ScraperExecutionGroup.objects.create(
            scraper=scraper,
            task_name="mpf_scraper_group",
            finish_datetime=datetime(2021, 10, 10, 8, 35, 21),
            status=STATUS_STARTED,
        )

        ScraperExecution.objects.bulk_create([
            ScraperExecution(
                scraper_execution_group=scraper_group_exec,
                task_id="352c6526-3153-11ec-8d3d-0242ac130003",
                finish_datetime=datetime(2021, 10, 10, 8, 35, 21),
            ),
            ScraperExecution(
                scraper_execution_group=scraper_group_exec,
                task_id="352c6742-3153-11ec-8d3d-0242ac130003",
                finish_datetime=datetime(2021, 10, 10, 8, 40, 10),
            ),
            ScraperExecution(
                scraper_execution_group=scraper_group_exec,
                task_id="352c6832-3153-11ec-8d3d-0242ac130003",
                finish_datetime=datetime(2021, 10, 10, 8, 50, 15),
            ),
        ])

        response = json.loads(self.client.get(
            f"{self.endpoint_base}/{scraper.id}/executions/",
            format='json'
        ).content)

        scraper_executions_group = response['results']

        self.assertEqual(
            1,
            len(scraper_executions_group),
        )

        self.assertEqual(
            3,
            len(scraper_executions_group[0]['scraper_executions']),
        )
