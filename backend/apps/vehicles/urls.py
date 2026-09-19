from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.vehicles.views import TransportModeViewSet, VehicleViewSet

router = DefaultRouter()
router.register(r"modes", TransportModeViewSet, basename="transportmode")
router.register(r"", VehicleViewSet, basename="vehicle")

urlpatterns = [
    path("", include(router.urls)),
]
