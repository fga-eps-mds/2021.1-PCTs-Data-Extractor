from django.db import models

class Keyword(models.Model):
    keyword = models.CharField(
        "Keyword",
        max_length=500,
        unique=True,
        null=False
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.keyword
