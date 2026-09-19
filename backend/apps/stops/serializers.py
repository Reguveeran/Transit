from rest_framework import serializers
from apps.stops.models import Stop
from apps.trips.models import StopTime


class StopSerializer(serializers.ModelSerializer):
    mode_name = serializers.CharField(source="transport_mode.name", read_only=True)

    class Meta:
        model = Stop
        fields = [
            "id",
            "stop_id",
            "name",
            "code",
            "latitude",
            "longitude",
            "zone_id",
            "transport_mode",
            "mode_name",
            "is_active",
        ]


class StopArrivalSerializer(serializers.ModelSerializer):
    trip_id = serializers.CharField(source="trip.trip_id", read_only=True)
    headsign = serializers.CharField(source="trip.headsign", read_only=True)
    route_short_name = serializers.CharField(source="trip.route.short_name", read_only=True)
    route_color = serializers.CharField(source="trip.route.color", read_only=True)
    vehicle_id = serializers.CharField(source="trip.vehicle.vehicle_id", default=None, read_only=True)
    delay_seconds = serializers.IntegerField(source="trip.vehicle.delay_seconds", default=0, read_only=True)

    class Meta:
        model = StopTime
        fields = [
            "trip_id",
            "headsign",
            "route_short_name",
            "route_color",
            "vehicle_id",
            "delay_seconds",
            "stop_sequence",
            "arrival_time",
            "departure_time",
        ]
