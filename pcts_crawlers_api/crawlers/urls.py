from django.urls import include, path
from rest_framework_nested import routers  # as nested_routers
from crawlers import views
from crawlers.views import CrawlerExecutorViewSet
from crawlers.views import CrawlerViewSet
from crawlers.views import CrawlerExecutionGroupViewSet

app_name = 'crawlers'
router = routers.DefaultRouter()
router.register(r'crawlers', views.CrawlerViewSet)

crawler_routes = routers.NestedSimpleRouter(
    router, r'crawlers', lookup='crawler'
)

crawler_routes.register(
    r'executions', views.CrawlerExecutionGroupViewSet,
    basename='crawler-executions'
)


urlpatterns = [
    path(r'', include(router.urls)),
    path(r'', include(crawler_routes.urls)),
    path('crawler-start', CrawlerExecutorViewSet.as_view(), name='crawler-start'),
]
