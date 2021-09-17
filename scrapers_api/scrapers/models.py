from django.contrib.postgres.fields import ArrayField
from django.db import models


class Scraper(models.Model):
    url_root = models.CharField("Root Url", max_length=1024)
    site_name = models.CharField("Site Name", max_length=50)
    # search_steps = ArrayField(
    #     models.CharField(max_length=10, blank=True),
    # )
    next_button_xpath = models.CharField("Next Button (XPATH)", max_length=240)
    # allow_domains = ArrayField(
    #     models.CharField(max_length=10, blank=True),
    # )
    # allow_resources = ArrayField(
    #     models.CharField(max_length=10, blank=True),
    # )
    pagination_retries = models.IntegerField(default=1)
    pagination_delay = models.IntegerField(default=1)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name
