from rest_framework.test import APITestCase
from django.urls import reverse
from datetime import datetime
import json

from crawlers.models import Crawler
from crawlers.models import CrawlerExecution
from crawlers.models import CrawlerExecutionGroup
from crawlers.models import STARTED


class CrawlerEndpoint(APITestCase):

    def setUp(self):
        self.endpoint = '/api/crawlers/'

    def tearDown(self):
        Crawler.objects.all().delete()

    def test_list_all_crawlers(self):
        Crawler.objects.bulk_create([
            Crawler(site_name="mpf", url_root="www.mpf.mp.br",
                    task_name_prefix="mpf_crawler"),
            Crawler(site_name="incra", url_root="www.gov.br/incra/pt-br",
                    task_name_prefix="incra_crawler"),
            Crawler(site_name="tcu", url_root="pesquisa.apps.tcu.gov.br",
                    task_name_prefix="tcu_crawler"),
        ])

        response = json.loads(self.client.get(
            self.endpoint,
            format='json'
        ).content)

        self.assertEqual(
            3,
            len(response['results']),
        )


class CrawlerExecutionsEndpoint(APITestCase):

    def setUp(self):
        self.endpoint_base = '/api/crawlers'

    def tearDown(self):
        Crawler.objects.all().delete()

    def test_list_all_crawler_executions(self):
        crawler = Crawler.objects.create(
            site_name="mpf",
            url_root="www.mpf.mp.br",
            task_name_prefix="mpf_crawler"
        )

        crawler_group_exec = CrawlerExecutionGroup.objects.create(
            crawler=crawler,
            task_name="mpf_crawler_group",
            finish_datetime=datetime(2021, 10, 10, 8, 35, 21),
            state=STARTED,
        )

        CrawlerExecution.objects.bulk_create([
            CrawlerExecution(
                crawler_execution_group=crawler_group_exec,
                task_id="352c6526-3153-11ec-8d3d-0242ac130003",
                finish_datetime=datetime(2021, 10, 10, 8, 35, 21),
            ),
            CrawlerExecution(
                crawler_execution_group=crawler_group_exec,
                task_id="352c6742-3153-11ec-8d3d-0242ac130003",
                finish_datetime=datetime(2021, 10, 10, 8, 40, 10),
            ),
            CrawlerExecution(
                crawler_execution_group=crawler_group_exec,
                task_id="352c6832-3153-11ec-8d3d-0242ac130003",
                finish_datetime=datetime(2021, 10, 10, 8, 50, 15),
            ),
        ])

        response = json.loads(self.client.get(
            f"{self.endpoint_base}/{crawler.id}/executions/",
            format='json'
        ).content)

        crawler_executions_group = response['results']

        self.assertEqual(
            1,
            len(crawler_executions_group),
        )

        self.assertEqual(
            3,
            len(crawler_executions_group[0]['crawler_executions']),
        )
