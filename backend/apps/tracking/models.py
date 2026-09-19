import uuid
from django.db import models


class VehiclePosition(models.Model):
    vehicle = models.ForeignKey(
        "vehicles.Vehicle",
        on_delete=models.CASCADE,
        related_name="positions",
    )
    trip = models.ForeignKey(
        "trips.Trip",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="positions",
    )
    latitude = models.FloatField(db_index=True)
    longitude = models.FloatField(db_index=True)
    speed = models.FloatField(default=0.0)
    heading = models.FloatField(default=0.0)
    status = models.CharField(max_length=30, default="MOVING")
    occupancy_status = models.CharField(max_length=30, blank=True, default="MANY_SEATS_AVAILABLE")
    delay_seconds = models.IntegerField(default=0)
    timestamp = models.DateTimeField(db_index=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "vehicle_positions"
        indexes = [
            models.Index(fields=["vehicle", "timestamp"]),
            models.Index(fields=["latitude", "longitude"]),
            models.Index(fields=["timestamp"]),
        ]
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.vehicle.vehicle_id} @ ({self.latitude}, {self.longitude}) [{self.timestamp}]"


class TransportEvent(models.Model):
    event_id = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    vehicle_id = models.CharField(max_length=64, db_index=True)
    mode = models.CharField(max_length=30)
    route_id = models.CharField(max_length=64, blank=True)
    source = models.CharField(max_length=50, default="simulator")
    payload = models.JSONField(help_text="Full normalized transport.event.v1 JSON payload.")
    received_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "transport_events"
        indexes = [
            models.Index(fields=["vehicle_id", "received_at"]),
            models.Index(fields=["mode", "received_at"]),
        ]
        ordering = ["-received_at"]

    def __str__(self):
        return f"Event {self.event_id} ({self.vehicle_id} - {self.mode})"
