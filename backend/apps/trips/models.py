from django.db import models


class Trip(models.Model):
    STATUS_CHOICES = (
        ("SCHEDULED", "Scheduled"),
        ("IN_PROGRESS", "In Progress"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    )

    trip_id = models.CharField(max_length=64, unique=True, db_index=True)
    route = models.ForeignKey(
        "routes.Route",
        on_delete=models.CASCADE,
        related_name="trips",
    )
    vehicle = models.ForeignKey(
        "vehicles.Vehicle",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="trips",
    )
    service_id = models.CharField(max_length=64, default="DAILY")
    headsign = models.CharField(max_length=150)  # e.g. "Central Station via Airport"
    direction = models.IntegerField(default=0, help_text="0 for outbound, 1 for inbound")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="SCHEDULED")
    scheduled_start = models.DateTimeField(null=True, blank=True)
    scheduled_end = models.DateTimeField(null=True, blank=True)
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "trips"
        ordering = ["-scheduled_start"]

    def __str__(self):
        return f"{self.trip_id} - {self.headsign}"


class StopTime(models.Model):
    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name="stop_times",
    )
    stop = models.ForeignKey(
        "stops.Stop",
        on_delete=models.CASCADE,
        related_name="stop_times",
    )
    stop_sequence = models.PositiveIntegerField()
    arrival_time = models.TimeField()
    departure_time = models.TimeField()
    pickup_type = models.IntegerField(default=0)
    drop_off_type = models.IntegerField(default=0)

    class Meta:
        db_table = "stop_times"
        unique_together = ("trip", "stop_sequence")
        ordering = ["trip", "stop_sequence"]

    def __str__(self):
        return f"{self.trip.trip_id} - Stop #{self.stop_sequence}: {self.stop.name}"
