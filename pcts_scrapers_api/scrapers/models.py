from django.db import models

STATUS_STARTED = 1
STATUS_SUCCESS = 2
STATUS_FAILED = 3

STATUS_CHOICES = [
    (STATUS_STARTED, "STARTED"),
    (STATUS_SUCCESS, "SUCCESS"),
    (STATUS_FAILED, "FAILED")
]


class Scraper(models.Model):
    site_name = models.CharField("Site Name", unique=True, max_length=100)
    url_root = models.CharField("Root Url", unique=True, max_length=1024)
    task_name_prefix = models.CharField(
        "Task Name Prefix",
        unique=True,
        max_length=50
    )
    js_search_steps = models.JSONField(
        "JS Search Steps (JSON List of Objects (elem_type, xpath, action))",
        null=True
    )
    next_button_xpath = models.CharField(
        "Next Button XPATH",
        max_length=500,
        null=True
    )
    allowed_domains = models.JSONField(
        "Allowed Domains (JSON List of strings)",
        null=True
    )
    allowed_paths = models.JSONField(
        "Allowed Paths (JSON List of strings)",
        null=True
    )
    restrict_xpaths = models.JSONField(
        "Restrict by Xpath (JSON List of strings)",
        null=True
    )
    restrict_css = models.JSONField(
        "Restrict by CSS (Json List of strings)",
        null=True
    )
    content_xpath = models.JSONField(
        "Content XPATH (JSON Object (any key-value))",
        null=True
    )
    query_string_params = models.JSONField(
        "Query String Params (JSON List Object (param, value))",
        null=True
    )
    pagination_retries = models.IntegerField(
        "Pagination Retries",
        default=3,
        null=True
    )
    pagination_delay = models.IntegerField(
        "Pagination Delay",
        default=3,
        null=True
    )
    page_load_timeout = models.IntegerField(
        "Page Load Delay",
        default=3,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.site_name


class ScraperExecutionGroup(models.Model):
    scraper = models.ForeignKey(
        Scraper,
        on_delete=models.CASCADE,
        related_name="scraper_executions_group"
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


class ScraperExecution(models.Model):
    scraper_execution_group = models.ForeignKey(
        ScraperExecutionGroup,
        on_delete=models.CASCADE,
        related_name="scraper_executions_keywords"
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
