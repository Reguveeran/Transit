from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.tracking.views import VehiclePositionViewSet, TransportEventViewSet

router = DefaultRouter()
router.register(r"positions", VehiclePositionViewSet, basename="position")
router.register(r"events", TransportEventViewSet, basename="event")

urlpatterns = [
    path("", include(router.urls)),
]
