from datetime import datetime
from django.test import TestCase
from crawlers.models import Crawler
from crawlers.models import CrawlerExecution
from crawlers.models import CrawlerExecutionGroup
from crawlers.models import STARTED, SUCCESS, FAILURE


class TestCrawlerModel(TestCase):

    def test_document_creation(self):
        site_name = "mpf"
        url_root = "www.mpf.mp.br"
        task_name_prefix = "mpf_crawler"

        crawler = Crawler.objects.create(
            site_name=site_name,
            url_root=url_root,
            task_name_prefix=task_name_prefix,
        )

        self.assertEqual(site_name, crawler.site_name)
        self.assertEqual(url_root, crawler.url_root)
        self.assertEqual(task_name_prefix, crawler.task_name_prefix)
        self.assertIsNotNone(crawler.created_at)


class TestCrawlerExecutionGroupModel(TestCase):

    def test_document_creation(self):
        crawler_model = Crawler.objects.create(
            site_name="mpf",
            url_root="www.mpf.mp.br",
            task_name_prefix="mpf_crawler",
        )

        crawler = crawler_model
        task_name = "mpf_crawler_group"
        finish_datetime = datetime(2021, 10, 10, 8, 34, 56)
        state = SUCCESS

        crawler_execution_group = CrawlerExecutionGroup.objects.create(
            crawler=crawler,
            task_name=task_name,
            finish_datetime=finish_datetime,
            state=state,
        )

        self.assertEqual(crawler.id, crawler_execution_group.crawler.id)
        self.assertEqual(task_name, crawler_execution_group.task_name)
        self.assertEqual(
            finish_datetime, crawler_execution_group.finish_datetime)
        self.assertEqual(state, crawler_execution_group.state)
        self.assertIsNotNone(crawler_execution_group.start_datetime)


class TestCrawlerExecutionModel(TestCase):

    def test_document_creation(self):
        crawler_model = Crawler.objects.create(
            site_name="mpf",
            url_root="www.mpf.mp.br",
            task_name_prefix="mpf_crawler",
        )

        crawler_execution_group_model = CrawlerExecutionGroup.objects.create(
            crawler=crawler_model,
            task_name="mpf_crawler_group",
            finish_datetime=datetime(2021, 10, 10, 8, 35, 21),
            state=STARTED,
        )

        crawler_execution_group = crawler_execution_group_model
        task_id = "ec7a5f20-314f-11ec-8d3d-0242ac130003"
        task_name = "mpf_crawler_keyword"
        finish_datetime = datetime.now()
        keyword = "quilombolas"
        state = FAILURE
        scraped_pages = 40
        saved_records = 37
        dropped_records = 3
        error_log = "error"

        crawler_execution = CrawlerExecution.objects.create(
            crawler_execution_group=crawler_execution_group,
            task_id=task_id,
            task_name=task_name,
            finish_datetime=finish_datetime,
            keyword=keyword,
            state=state,
            scraped_pages=scraped_pages,
            saved_records=saved_records,
            dropped_records=dropped_records,
            error_log=error_log,
        )

        self.assertEqual(crawler_execution_group.id,
                         crawler_execution.crawler_execution_group.id)
        self.assertEqual(task_id, crawler_execution.task_id)
        self.assertEqual(task_name, crawler_execution.task_name)
        self.assertEqual(finish_datetime, crawler_execution.finish_datetime)
        self.assertEqual(keyword, crawler_execution.keyword)
        self.assertEqual(state, crawler_execution.state)
        self.assertEqual(scraped_pages, crawler_execution.scraped_pages)
        self.assertEqual(saved_records, crawler_execution.saved_records)
        self.assertEqual(dropped_records, crawler_execution.dropped_records)
        self.assertEqual(error_log, crawler_execution.error_log)
        self.assertIsNotNone(crawler_execution.start_datetime)
