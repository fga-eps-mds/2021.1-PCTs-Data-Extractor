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

        Crawler.objects.bulk_create([
            Crawler(site_name="mpf", url_root="www.mpf.mp.br",
                    task_name="mpf_crawler"),
            Crawler(site_name="incra", url_root="www.gov.br/incra/pt-br",
                    task_name="incra_crawler"),
            Crawler(site_name="tcu", url_root="pesquisa.apps.tcu.gov.br",
                    task_name="tcu_crawler"),
        ])

        self.crawler = {
            "site_name":"ibama",
            "url_root":"www.gov.br/ibama/pt-br",
            "task_name":"ibama_crawler",
        }

    def tearDown(self):
        Crawler.objects.all().delete()

    def test_list_all_crawlers(self):
        response = json.loads(self.client.get(
            self.endpoint,
            format='json'
        ).content)

        self.assertEqual(
            3,
            len(response['results']),
        )

    def test_create(self):
        response = self.client.post(
            self.endpoint,
            self.crawler
        )

        json_response = json.loads(response.content)
        
        self.assertEqual(201, response.status_code)
        self.assertEqual(self.crawler['site_name'], json_response['site_name'])
        self.assertEqual(self.crawler['url_root'], json_response['url_root'])
        self.assertEqual(self.crawler['task_name'], json_response['task_name'])

        return json_response['id']

    def test_get(self):
        crawler_id = self.test_create()

        response = self.client.get(
            f"{self.endpoint}{crawler_id}/",
            format='json'
        )

        json_response = json.loads(response.content)

        self.assertEqual(200, response.status_code)
        self.assertEqual(self.crawler['site_name'], json_response['site_name'])
        self.assertEqual(self.crawler['url_root'], json_response['url_root'])
        self.assertEqual(self.crawler['task_name'], json_response['task_name'])

        return json_response

    def test_update(self):
        crawler_id = self.test_create()

        crawler_update = {
            "site_name":"ibge",
            "url_root":"www.ibge.gov.br",
            "task_name":"ibge_crawler",
        }
        updated_response = self.client.put(
            f"{self.endpoint}{crawler_id}/",
            crawler_update
        )

        json_response = json.loads(updated_response.content)

        self.assertEqual(200, updated_response.status_code)
        self.assertEqual(crawler_update['site_name'], json_response['site_name'])
        self.assertEqual(crawler_update['url_root'], json_response['url_root'])
        self.assertEqual(crawler_update['task_name'], json_response['task_name'])
        
    def test_delete(self):
        crawler_id = self.test_create()
        response = self.client.delete(
            f"{self.endpoint}{crawler_id}/",
            format='json'
        )
        self.assertEqual(204, response.status_code)

class CrawlerExecutionsEndpoint(APITestCase):

    def setUp(self):
        self.endpoint_base = '/api/crawlers'
        self.crawler = Crawler.objects.create(
            site_name="mpf",
            url_root="www.mpf.mp.br",
            task_name="mpf_crawler"
        )

        self.crawler_group_exec = CrawlerExecutionGroup.objects.create(
            crawler=self.crawler,
            task_name="mpf_crawler_group",
            finish_datetime=datetime(2021, 10, 10, 8, 35, 21),
            state=STARTED,
        )

        CrawlerExecution.objects.bulk_create([
            CrawlerExecution(
                crawler_execution_group=self.crawler_group_exec,
                task_id="352c6526-3153-11ec-8d3d-0242ac130003",
                finish_datetime=datetime(2021, 10, 10, 8, 35, 21),
            ),
            CrawlerExecution(
                crawler_execution_group=self.crawler_group_exec,
                task_id="352c6742-3153-11ec-8d3d-0242ac130003",
                finish_datetime=datetime(2021, 10, 10, 8, 40, 10),
            ),
            CrawlerExecution(
                crawler_execution_group=self.crawler_group_exec,
                task_id="352c6832-3153-11ec-8d3d-0242ac130003",
                finish_datetime=datetime(2021, 10, 10, 8, 50, 15),
            ),
        ])

    def tearDown(self):
        Crawler.objects.all().delete()

    def test_list_all_crawler_executions(self):
        response = json.loads(self.client.get(
            f"{self.endpoint_base}/{self.crawler.id}/executions/",
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
