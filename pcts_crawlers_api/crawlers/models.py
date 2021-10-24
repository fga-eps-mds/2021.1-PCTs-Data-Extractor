from django.db import models

STATUS_STARTED = 1
STATUS_SUCCESS = 2
STATUS_FAILED = 3

STATUS_CHOICES = [
    (STATUS_STARTED, "STARTED"),
    (STATUS_SUCCESS, "SUCCESS"),
    (STATUS_FAILED, "FAILED")
]


class Crawler(models.Model):
    site_name = models.CharField("Site Name", unique=True, max_length=100)
    url_root = models.CharField("Root Url", unique=True, max_length=1024)
    task_name_prefix = models.CharField(
        "Task Name Prefix",
        unique=True,
        max_length=50
    )
    allowed_domains = models.JSONField(
        "Allowed Domains (JSON List of strings)",
        null=True
    )
    allowed_paths = models.JSONField(
        "Allowed Paths (JSON List of strings)",
        null=True
    )
    qs_search_keyword_param = models.CharField(
        "Query String Params (JSON List Object (param, value))",
        null=True,
        max_length=500
    )
    retries = models.IntegerField(
        "Retries",
        default=3,
        null=True
    )
    page_load_timeout = models.IntegerField(
        "Page Load Timeout",
        default=3,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.site_name


class CrawlerExecutionGroup(models.Model):
    crawler = models.ForeignKey(
        Crawler,
        on_delete=models.CASCADE,
        related_name="crawler_executions_group"
    )
    task_name = models.CharField("Task Name", max_length=100)
    start_datetime = models.DateTimeField("Start Datetime", auto_now_add=True)
    finish_datetime = models.DateTimeField("End Datetime", null=True)
    status = models.IntegerField(
        "Execution Status",
        choices=STATUS_CHOICES,
        default=1
    )

    def __str__(self):
        return self.task_name


class CrawlerExecution(models.Model):
    crawler_execution_group = models.ForeignKey(
        CrawlerExecutionGroup,
        on_delete=models.CASCADE,
        related_name="crawler_executions"
    )
    task_id = models.UUIDField("Task Run UUID")
    task_name = models.CharField("Task Name", max_length=100)
    start_datetime = models.DateTimeField("Start Datetime", auto_now_add=True)
    finish_datetime = models.DateTimeField("Finish Datetime", null=True)
    keyword = models.CharField("Keyword", max_length=1024)
    status = models.IntegerField(
        "Execution Status",
        choices=STATUS_CHOICES,
        default=1
    )
    scraped_pages = models.IntegerField(null=True)
    saved_records = models.IntegerField(null=True)
    dropped_records = models.IntegerField(null=True)
    error_log = models.TextField(null=True)

    def __str__(self):
        return self.task_name
