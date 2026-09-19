from rest_framework import serializers
from apps.trips.models import Trip, StopTime


class StopTimeNestedSerializer(serializers.ModelSerializer):
    stop_name = serializers.CharField(source="stop.name", read_only=True)
    latitude = serializers.FloatField(source="stop.latitude", read_only=True)
    longitude = serializers.FloatField(source="stop.longitude", read_only=True)

    class Meta:
        model = StopTime
        fields = [
            "stop_sequence",
            "stop",
            "stop_name",
            "latitude",
            "longitude",
            "arrival_time",
            "departure_time",
        ]


class TripSerializer(serializers.ModelSerializer):
    route_short_name = serializers.CharField(source="route.short_name", read_only=True)
    route_color = serializers.CharField(source="route.color", read_only=True)
    vehicle_id_assigned = serializers.CharField(source="vehicle.vehicle_id", read_only=True, default=None)
    stop_times = StopTimeNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Trip
        fields = [
            "id",
            "trip_id",
            "route",
            "route_short_name",
            "route_color",
            "vehicle",
            "vehicle_id_assigned",
            "service_id",
            "headsign",
            "direction",
            "status",
            "scheduled_start",
            "scheduled_end",
            "stop_times",
        ]
