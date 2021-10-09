from django.urls import include, path
from rest_framework import routers
from scrapers import views
from scrapers.views import ScraperExecutorViewSet
from scrapers.views import ScraperViewSet

app_name = 'scrapers'
router = routers.DefaultRouter()
router.register(r'', views.ScraperViewSet, basename='DocumentViewSet')

urlpatterns = [
    path('start/', ScraperExecutorViewSet.start, name='scraper-start'),
    path(r'', include(router.urls)),
]
