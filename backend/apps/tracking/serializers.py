from rest_framework import serializers
from apps.tracking.models import VehiclePosition, TransportEvent


class VehiclePositionSerializer(serializers.ModelSerializer):
    vehicle_id = serializers.CharField(source="vehicle.vehicle_id", read_only=True)

    class Meta:
        model = VehiclePosition
        fields = [
            "id",
            "vehicle_id",
            "trip",
            "latitude",
            "longitude",
            "speed",
            "heading",
            "status",
            "occupancy_status",
            "delay_seconds",
            "timestamp",
            "recorded_at",
        ]


class TransportEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportEvent
        fields = [
            "event_id",
            "vehicle_id",
            "mode",
            "route_id",
            "source",
            "payload",
            "received_at",
        ]
