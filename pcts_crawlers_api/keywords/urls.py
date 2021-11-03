from django.urls import include, path
from rest_framework_nested import routers  # as nested_routers
from keywords.views import KeywordViewSet


app_name = 'keywords'
router = routers.DefaultRouter()
router.register(r'keywords', KeywordViewSet)


urlpatterns = [
    path(r'', include(router.urls)),
]
