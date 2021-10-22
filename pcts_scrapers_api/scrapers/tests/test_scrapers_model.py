from datetime import datetime
from django.test import TestCase
from scrapers.models import Scraper
from scrapers.models import ScraperExecution
from scrapers.models import ScraperExecutionGroup
from scrapers.models import STATUS_STARTED, STATUS_SUCCESS, STATUS_FAILED


class TestScraperModel(TestCase):

    def test_document_creation(self):
        site_name = "mpf"
        url_root = "www.mpf.mp.br"
        task_name_prefix = "mpf_scraper"

        scraper = Scraper.objects.create(
            site_name=site_name,
            url_root=url_root,
            task_name_prefix=task_name_prefix,
        )

        self.assertEqual(site_name, scraper.site_name)
        self.assertEqual(url_root, scraper.url_root)
        self.assertEqual(task_name_prefix, scraper.task_name_prefix)
        self.assertIsNotNone(scraper.created_at)


class TestScraperExecutionGroupModel(TestCase):

    def test_document_creation(self):
        scraper_model = Scraper.objects.create(
            site_name="mpf",
            url_root="www.mpf.mp.br",
            task_name_prefix="mpf_scraper",
        )

        scraper = scraper_model
        task_name = "mpf_scraper_group"
        finish_datetime = datetime(2021, 10, 10, 8, 34, 56)
        status = STATUS_SUCCESS

        scraper_execution_group = ScraperExecutionGroup.objects.create(
            scraper=scraper,
            task_name=task_name,
            finish_datetime=finish_datetime,
            status=status,
        )

        self.assertEqual(scraper.id, scraper_execution_group.scraper.id)
        self.assertEqual(task_name, scraper_execution_group.task_name)
        self.assertEqual(
            finish_datetime, scraper_execution_group.finish_datetime)
        self.assertEqual(status, scraper_execution_group.status)
        self.assertIsNotNone(scraper_execution_group.start_datetime)


class TestScraperExecutionModel(TestCase):

    def test_document_creation(self):
        scraper_model = Scraper.objects.create(
            site_name="mpf",
            url_root="www.mpf.mp.br",
            task_name_prefix="mpf_scraper",
        )

        scraper_execution_group_model = ScraperExecutionGroup.objects.create(
            scraper=scraper_model,
            task_name="mpf_scraper_group",
            finish_datetime=datetime(2021, 10, 10, 8, 35, 21),
            status=STATUS_STARTED,
        )

        scraper_execution_group = scraper_execution_group_model
        task_id = "ec7a5f20-314f-11ec-8d3d-0242ac130003"
        task_name = "mpf_scraper_keyword"
        finish_datetime = datetime.now()
        keyword = "quilombolas"
        status = STATUS_FAILED
        scraped_pages = 40
        saved_records = 37
        dropped_records = 3
        error_log = "error"

        scraper_execution = ScraperExecution.objects.create(
            scraper_execution_group=scraper_execution_group,
            task_id=task_id,
            task_name=task_name,
            finish_datetime=finish_datetime,
            keyword=keyword,
            status=status,
            scraped_pages=scraped_pages,
            saved_records=saved_records,
            dropped_records=dropped_records,
            error_log=error_log,
        )

        self.assertEqual(scraper_execution_group.id,
                         scraper_execution.scraper_execution_group.id)
        self.assertEqual(task_id, scraper_execution.task_id)
        self.assertEqual(task_name, scraper_execution.task_name)
        self.assertEqual(finish_datetime, scraper_execution.finish_datetime)
        self.assertEqual(keyword, scraper_execution.keyword)
        self.assertEqual(status, scraper_execution.status)
        self.assertEqual(scraped_pages, scraper_execution.scraped_pages)
        self.assertEqual(saved_records, scraper_execution.saved_records)
        self.assertEqual(dropped_records, scraper_execution.dropped_records)
        self.assertEqual(error_log, scraper_execution.error_log)
        self.assertIsNotNone(scraper_execution.start_datetime)
