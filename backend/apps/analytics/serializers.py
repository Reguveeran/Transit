from rest_framework import serializers
from apps.analytics.models import DelayAnalytics, FleetStats


class DelayAnalyticsSerializer(serializers.ModelSerializer):
    route_short_name = serializers.CharField(source="route.short_name", read_only=True)
    route_long_name = serializers.CharField(source="route.long_name", read_only=True)

    class Meta:
        model = DelayAnalytics
        fields = [
            "id",
            "route",
            "route_short_name",
            "route_long_name",
            "date",
            "avg_delay_seconds",
            "max_delay_seconds",
            "min_delay_seconds",
            "sample_count",
            "on_time_percentage",
            "calculated_at",
        ]


class FleetStatsSerializer(serializers.ModelSerializer):
    mode_name = serializers.CharField(source="transport_mode.name", read_only=True)
    mode_display = serializers.CharField(source="transport_mode.display_name", read_only=True)

    class Meta:
        model = FleetStats
        fields = [
            "id",
            "transport_mode",
            "mode_name",
            "mode_display",
            "total_vehicles",
            "active_vehicles",
            "delayed_vehicles",
            "average_speed_kmh",
            "recorded_at",
        ]
