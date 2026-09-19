from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.stops.models import Stop
from apps.stops.serializers import StopSerializer, StopArrivalSerializer
from apps.trips.models import StopTime


class StopViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Stop.objects.select_related("transport_mode").all()
    serializer_class = StopSerializer
    lookup_field = "stop_id"
    filterset_fields = ["is_active", "zone_id", "transport_mode__name"]
    search_fields = ["stop_id", "name", "code"]
    ordering_fields = ["name", "stop_id"]

    @action(detail=True, methods=["get"])
    def arrivals(self, request, stop_id=None):
        stop = self.get_object()
        # Find scheduled stop times for this stop
        stop_times = (
            StopTime.objects.filter(stop=stop)
            .select_related("trip", "trip__route", "trip__vehicle")
            .order_by("arrival_time")[:10]
        )
        serializer = StopArrivalSerializer(stop_times, many=True)
        return Response(serializer.data)
