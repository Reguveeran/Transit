from rest_framework import viewsets
from apps.tracking.models import VehiclePosition, TransportEvent
from apps.tracking.serializers import VehiclePositionSerializer, TransportEventSerializer


class VehiclePositionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = VehiclePosition.objects.select_related("vehicle").all()
    serializer_class = VehiclePositionSerializer
    filterset_fields = ["vehicle__vehicle_id", "status"]
    ordering_fields = ["timestamp", "recorded_at"]


class TransportEventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TransportEvent.objects.all()
    serializer_class = TransportEventSerializer
    lookup_field = "event_id"
    filterset_fields = ["vehicle_id", "mode", "source"]
    ordering_fields = ["received_at"]
