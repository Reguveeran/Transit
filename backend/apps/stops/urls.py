from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.stops.views import StopViewSet

router = DefaultRouter()
router.register(r"", StopViewSet, basename="stop")

urlpatterns = [
    path("", include(router.urls)),
]
