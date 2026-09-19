from rest_framework import serializers
from apps.alerts.models import Alert, ServiceAlert


class AlertSerializer(serializers.ModelSerializer):
    vehicle_id = serializers.CharField(source="vehicle.vehicle_id", read_only=True, default=None)
    route_short_name = serializers.CharField(source="route.short_name", read_only=True, default=None)

    class Meta:
        model = Alert
        fields = [
            "id",
            "alert_id",
            "alert_type",
            "severity",
            "vehicle",
            "vehicle_id",
            "route",
            "route_short_name",
            "message",
            "details",
            "latitude",
            "longitude",
            "is_resolved",
            "created_at",
            "resolved_at",
        ]


class ServiceAlertSerializer(serializers.ModelSerializer):
    affected_routes_details = serializers.SerializerMethodField()

    class Meta:
        model = ServiceAlert
        fields = [
            "id",
            "alert_id",
            "title",
            "header_text",
            "description_text",
            "cause",
            "effect",
            "affected_routes",
            "affected_routes_details",
            "is_active",
            "active_period_start",
            "active_period_end",
            "created_at",
        ]

    def get_affected_routes_details(self, obj):
        return [
            {"route_id": r.route_id, "short_name": r.short_name, "color": r.color}
            for r in obj.affected_routes.all()
        ]
