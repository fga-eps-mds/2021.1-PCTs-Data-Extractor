from django.urls import include, path
# from rest_framework import routers
from rest_framework_nested import routers  # as nested_routers
from scrapers import views
# from scrapers.views import ScraperExecutorViewSet
from scrapers.views import ScraperViewSet
from scrapers.views import ScraperExecutionGroupViewSet

app_name = 'scrapers'
router = routers.DefaultRouter()
router.register(r'scrapers', views.ScraperViewSet)

# scrapers_router = routers.NestedSimpleRouter(router, r'scrapers', lookup='scraper')
# scrapers_router.register(r'executions', views.ScraperExecutionGroupViewSet, basename='scraper-executions')

router.register(r'executions', views.ScraperExecutionGroupViewSet,
                basename='scraper-executions')

# urlpatterns = [
#     path(r'', include(router.urls)),
#     path(r'', include(scrapers_router.urls)),
#     # path('start', ScraperExecutorViewSet.start, name='scraper-start'),
# ]
