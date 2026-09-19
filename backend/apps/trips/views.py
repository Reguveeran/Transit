from rest_framework import viewsets
from apps.trips.models import Trip
from apps.trips.serializers import TripSerializer


class TripViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Trip.objects.select_related("route", "vehicle").prefetch_related("stop_times__stop").all()
    serializer_class = TripSerializer
    lookup_field = "trip_id"
    filterset_fields = ["status", "route__route_id", "service_id"]
    search_fields = ["trip_id", "headsign"]
    ordering_fields = ["scheduled_start", "trip_id"]
