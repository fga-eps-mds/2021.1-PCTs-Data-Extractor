from django.urls import include, path
from rest_framework import routers
from scrapers import views
from scrapers.views import ScraperExecutorViewSet
from scrapers.views import ScraperViewSet
from scrapers.views import ScraperExecutionGroupViewSet

app_name = 'scrapers'
router = routers.DefaultRouter()
router.register(r'', views.ScraperViewSet, basename='scraper')
router.register(
    r'executions',
    views.ScraperExecutionGroupViewSet,
    basename='scraper-executions',
)

urlpatterns = [
    path('start/', ScraperExecutorViewSet.start, name='scraper-start'),
    path(r'', include(router.urls)),
]
