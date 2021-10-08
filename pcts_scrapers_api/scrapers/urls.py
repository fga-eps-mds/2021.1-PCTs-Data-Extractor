from django.urls import path
from scrapers import views
from scrapers.views import ScraperExecutor

app_name = 'scrapers'
urlpatterns = [
    path('start/', ScraperExecutor.start, name='scraper-start'),
]
