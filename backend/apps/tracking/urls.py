from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.tracking.views import VehiclePositionViewSet, TransportEventViewSet
from apps.tracking.views_transitland import (
    live_telemetry_status,
    list_transitland_operators,
    list_transitland_feeds,
    import_transitland_operator,
)

router = DefaultRouter()
router.register(r"positions", VehiclePositionViewSet, basename="position")
router.register(r"events", TransportEventViewSet, basename="event")

urlpatterns = [
    path("status/", live_telemetry_status, name="live-telemetry-status"),
    path("transitland/operators/", list_transitland_operators, name="transitland-operators"),
    path("transitland/feeds/", list_transitland_feeds, name="transitland-feeds"),
    path("transitland/import/", import_transitland_operator, name="transitland-import"),
    path("", include(router.urls)),
]
