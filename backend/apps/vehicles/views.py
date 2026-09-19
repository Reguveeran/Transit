from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.vehicles.models import TransportMode, Vehicle
from apps.vehicles.serializers import (
    TransportModeSerializer,
    VehicleSerializer,
    VehicleLocationSerializer,
)


class TransportModeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TransportMode.objects.filter(is_active=True)
    serializer_class = TransportModeSerializer


class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.select_related("transport_mode", "current_route").all()
    serializer_class = VehicleSerializer
    lookup_field = "vehicle_id"
    filterset_fields = ["status", "is_active", "transport_mode__name", "current_route__route_id"]
    search_fields = ["vehicle_id", "label", "license_plate"]
    ordering_fields = ["vehicle_id", "current_speed", "delay_seconds", "last_seen"]

    @action(detail=True, methods=["get"])
    def location(self, request, vehicle_id=None):
        vehicle = self.get_object()
        serializer = VehicleLocationSerializer(vehicle)
        return Response(serializer.data)
