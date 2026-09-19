from rest_framework import serializers
from apps.routes.models import Route
from apps.vehicles.serializers import VehicleSerializer


class RouteSerializer(serializers.ModelSerializer):
    mode_name = serializers.CharField(source="transport_mode.name", read_only=True)
    mode_display = serializers.CharField(source="transport_mode.display_name", read_only=True)

    class Meta:
        model = Route
        fields = [
            "id",
            "route_id",
            "transport_mode",
            "mode_name",
            "mode_display",
            "short_name",
            "long_name",
            "description",
            "color",
            "text_color",
            "is_active",
            "polyline_geojson",
        ]
