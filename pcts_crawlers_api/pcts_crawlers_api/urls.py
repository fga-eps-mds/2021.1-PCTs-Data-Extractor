from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from django.urls import include, path
from crawlers import views

from crawlers import urls as crawler_routes
from keywords import urls as keywords_routes
from rest_framework import routers

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urls = [
    path('', include('crawlers.urls', namespace="crawlers")),
    path('', include('keywords.urls', namespace="keywords")),
]

router = routers.DefaultRouter()
router.registry.extend(crawler_routes.router.registry)
router.registry.extend(keywords_routes.router.registry)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include(router.urls)),
    path('api/', include(urls)),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
