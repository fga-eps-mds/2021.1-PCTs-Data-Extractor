from datetime import datetime
from django.test import TestCase
from crawlers.models import Crawler
from crawlers.models import CrawlerExecution
from crawlers.models import CrawlerExecutionGroup
from crawlers.models import STARTED, SUCCESS, FAILURE


class TestCrawlerModel(TestCase):

    def setUp(self):
        self.crawler = Crawler.objects.create(
            site_name="mpf",
            url_root="www.mpf.mp.br",
            task_name="mpf_crawler",
        )

    def test_document_creation(self):
        site_name = "mpf"
        url_root = "www.mpf.mp.br"
        task_name = "mpf_crawler"

        self.assertEqual(site_name, self.crawler.site_name)
        self.assertEqual(url_root, self.crawler.url_root)
        self.assertEqual(task_name, self.crawler.task_name)
        self.assertIsNotNone(self.crawler.created_at)

    def test_document_get(self):
        crawler = Crawler.objects.filter(id=self.crawler.id).get()
        self.assertEqual(crawler, self.crawler)

    def test_document_update(self):
        site_name = "incra"
        url_root = "www.gov.br/incra/pt-br"
        task_name = "incra_crawler"

        self.crawler.site_name = site_name
        self.crawler.url_root = url_root
        self.crawler.task_name = task_name
        self.crawler.save()
        
        updated_crawler = Crawler.objects.filter(id=self.crawler.id).get()
        self.assertEqual(site_name, updated_crawler.site_name)
        self.assertEqual(url_root, updated_crawler.url_root)
        self.assertEqual(task_name, updated_crawler.task_name)

    def test_document_delete(self):
        self.crawler.delete()

        try:
            Crawler.objects.filter(id=self.crawler.id).get()
        except Crawler.DoesNotExist:
            self.assertTrue(True)


class TestCrawlerExecutionGroupModel(TestCase):
    def setUp(self):
        self.crawler_model = Crawler.objects.create(
            site_name="mpf",
            url_root="www.mpf.mp.br",
            task_name="mpf_crawler",
        )

        self.crawler_execution_group = CrawlerExecutionGroup.objects.create(
            crawler=self.crawler_model,
            task_name="mpf_crawler_group",
            finish_datetime=datetime(2021, 10, 10, 8, 34, 56),
            state=SUCCESS,
        )

    def test_document_creation(self):
        crawler = self.crawler_model
        task_name = "mpf_crawler_group"
        finish_datetime = datetime(2021, 10, 10, 8, 34, 56)
        state = SUCCESS

        self.assertEqual(crawler.id, self.crawler_execution_group.crawler.id)
        self.assertEqual(task_name, self.crawler_execution_group.task_name)
        self.assertEqual(
            finish_datetime, self.crawler_execution_group.finish_datetime)
        self.assertEqual(state, self.crawler_execution_group.state)
        self.assertIsNotNone(self.crawler_execution_group.start_datetime)

    def test_document_get(self):
        crawler_execution_group = CrawlerExecutionGroup.objects.filter(id=self.crawler_execution_group.id).get()
        self.assertEqual(crawler_execution_group, self.crawler_execution_group)

    def test_document_update(self):
        crawler_model = Crawler.objects.create(
            site_name="incra",
            url_root="www.gov.br/incra/pt-br",
            task_name="incra_crawler",
        )

        self.crawler_execution_group.crawler = crawler_model
        self.crawler_execution_group.task_name = "incra_crawler_group"
        self.crawler_execution_group.finish_datetime = datetime(2021, 10, 14, 8, 34, 56)
        self.crawler_execution_group.state = SUCCESS
        self.crawler_execution_group.save()

        updated_crawler_execution_group = CrawlerExecutionGroup.objects.filter(id=self.crawler_execution_group.id).get()
        self.assertEqual(updated_crawler_execution_group, self.crawler_execution_group)

    def test_document_delete(self):
        self.crawler_execution_group.delete()

        try:
            CrawlerExecutionGroup.objects.filter(id=self.crawler_execution_group.id).get()
        except CrawlerExecutionGroup.DoesNotExist:
            self.assertTrue(True)


class TestCrawlerExecutionModel(TestCase):
    def setUp(self):
        self.crawler_model = Crawler.objects.create(
            site_name="mpf",
            url_root="www.mpf.mp.br",
            task_name="mpf_crawler",
        )

        self.crawler_execution_group_model = CrawlerExecutionGroup.objects.create(
            crawler=self.crawler_model,
            task_name="mpf_crawler_group",
            finish_datetime=datetime(2021, 10, 10, 8, 35, 21),
            state=STARTED,
        )

        self.crawler_execution = CrawlerExecution.objects.create(
            crawler_execution_group=self.crawler_execution_group_model,
            task_id="ec7a5f20-314f-11ec-8d3d-0242ac130003",
            task_name="mpf_crawler_keyword",
            finish_datetime=datetime(2021, 10, 10, 8, 40, 00),
            keyword="quilombolas",
            state=FAILURE,
            crawled_pages=40,
            saved_records=37,
            dropped_records=3,
            error_log="error",
        )

    def test_document_creation(self):
        crawler_execution_group = self.crawler_execution_group_model
        task_id = "ec7a5f20-314f-11ec-8d3d-0242ac130003"
        task_name = "mpf_crawler_keyword"
        finish_datetime = datetime(2021, 10, 10, 8, 40, 00)
        keyword = "quilombolas"
        state = FAILURE
        crawled_pages = 40
        saved_records = 37
        dropped_records = 3
        error_log = "error"

        self.assertEqual(crawler_execution_group.id,
                         self.crawler_execution.crawler_execution_group.id)
        self.assertEqual(task_id, self.crawler_execution.task_id)
        self.assertEqual(task_name, self.crawler_execution.task_name)
        self.assertEqual(finish_datetime, self.crawler_execution.finish_datetime)
        self.assertEqual(keyword, self.crawler_execution.keyword)
        self.assertEqual(state, self.crawler_execution.state)
        self.assertEqual(crawled_pages, self.crawler_execution.crawled_pages)
        self.assertEqual(saved_records, self.crawler_execution.saved_records)
        self.assertEqual(dropped_records, self.crawler_execution.dropped_records)
        self.assertEqual(error_log, self.crawler_execution.error_log)
        self.assertIsNotNone(self.crawler_execution.start_datetime)
