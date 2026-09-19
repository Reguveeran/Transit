from rest_framework import serializers
from apps.vehicles.models import TransportMode, Vehicle


class TransportModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportMode
        fields = ["id", "name", "display_name", "icon_name", "description", "is_active"]


class VehicleSerializer(serializers.ModelSerializer):
    mode_name = serializers.CharField(source="transport_mode.name", read_only=True)
    mode_display = serializers.CharField(source="transport_mode.display_name", read_only=True)
    route_short_name = serializers.CharField(source="current_route.short_name", read_only=True)

    class Meta:
        model = Vehicle
        fields = [
            "id",
            "vehicle_id",
            "transport_mode",
            "mode_name",
            "mode_display",
            "label",
            "license_plate",
            "capacity",
            "status",
            "occupancy_status",
            "current_latitude",
            "current_longitude",
            "current_speed",
            "current_heading",
            "current_route",
            "route_short_name",
            "current_trip",
            "delay_seconds",
            "last_seen",
            "is_active",
        ]


class VehicleLocationSerializer(serializers.ModelSerializer):
    mode_name = serializers.CharField(source="transport_mode.name", read_only=True)

    class Meta:
        model = Vehicle
        fields = [
            "vehicle_id",
            "mode_name",
            "current_latitude",
            "current_longitude",
            "current_speed",
            "current_heading",
            "status",
            "delay_seconds",
            "last_seen",
        ]
