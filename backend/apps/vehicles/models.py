from django.db import models
from django.utils import timezone


class TransportMode(models.Model):
    name = models.CharField(max_length=50, unique=True)  # e.g., "bus", "metro", "train", "ferry", "aircraft"
    display_name = models.CharField(max_length=100)
    icon_name = models.CharField(max_length=50, default="bus")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "transport_modes"
        ordering = ["name"]

    def __str__(self):
        return self.display_name


class Vehicle(models.Model):
    STATUS_CHOICES = (
        ("SCHEDULED", "Scheduled"),
        ("BOARDING", "Boarding"),
        ("MOVING", "Moving"),
        ("STOPPED", "Stopped"),
        ("CONGESTED", "Congested"),
        ("OFFLINE", "Offline"),
        ("EMERGENCY", "Emergency"),
    )

    OCCUPANCY_CHOICES = (
        ("EMPTY", "Empty"),
        ("MANY_SEATS_AVAILABLE", "Many Seats Available"),
        ("FEW_SEATS_AVAILABLE", "Few Seats Available"),
        ("STANDING_ROOM_ONLY", "Standing Room Only"),
        ("FULL", "Full"),
        ("NOT_ACCEPTING_PASSENGERS", "Not Accepting Passengers"),
    )

    vehicle_id = models.CharField(max_length=64, unique=True, db_index=True)
    transport_mode = models.ForeignKey(
        TransportMode,
        on_delete=models.PROTECT,
        related_name="vehicles",
    )
    label = models.CharField(max_length=100, blank=True)
    license_plate = models.CharField(max_length=30, blank=True)
    capacity = models.PositiveIntegerField(default=50)

    # Real-time state fields
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="OFFLINE", db_index=True)
    occupancy_status = models.CharField(
        max_length=30,
        choices=OCCUPANCY_CHOICES,
        default="MANY_SEATS_AVAILABLE",
    )
    current_latitude = models.FloatField(null=True, blank=True)
    current_longitude = models.FloatField(null=True, blank=True)
    current_speed = models.FloatField(default=0.0)
    current_heading = models.FloatField(default=0.0)
    current_route = models.ForeignKey(
        "routes.Route",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="active_vehicles",
    )
    current_trip = models.ForeignKey(
        "trips.Trip",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="active_vehicles",
    )
    delay_seconds = models.IntegerField(default=0)
    last_seen = models.DateTimeField(null=True, blank=True, db_index=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "vehicles"
        indexes = [
            models.Index(fields=["current_latitude", "current_longitude"]),
            models.Index(fields=["status", "is_active"]),
        ]
        ordering = ["vehicle_id"]

    def __str__(self):
        return f"{self.vehicle_id} ({self.transport_mode.name})"

    @property
    def is_moving(self) -> bool:
        return self.status == "MOVING" and self.current_speed > 0.5
