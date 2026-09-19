import uuid
from django.db import models


class Alert(models.Model):
    ALERT_TYPES = (
        ("OVERSPEED", "Overspeed Violation"),
        ("UNEXPECTED_STOP", "Unexpected Vehicle Stop"),
        ("ROUTE_DEVIATION", "Route Deviation"),
        ("LONG_DELAY", "Excessive Delay"),
        ("VEHICLE_OFFLINE", "Vehicle Signal Lost / Offline"),
        ("EMERGENCY", "Vehicle Emergency Broadcast"),
    )

    SEVERITY_LEVELS = (
        ("INFO", "Informational"),
        ("WARNING", "Warning"),
        ("CRITICAL", "Critical"),
    )

    alert_id = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    alert_type = models.CharField(max_length=40, choices=ALERT_TYPES, db_index=True)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default="WARNING")
    vehicle = models.ForeignKey(
        "vehicles.Vehicle",
        on_delete=models.CASCADE,
        related_name="alerts",
        null=True,
        blank=True,
    )
    route = models.ForeignKey(
        "routes.Route",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="alerts",
    )
    message = models.TextField()
    details = models.JSONField(default=dict, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    is_resolved = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "alerts"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.severity}] {self.get_alert_type_display()} - {self.vehicle_id or 'System'}"


class ServiceAlert(models.Model):
    alert_id = models.CharField(max_length=64, unique=True, db_index=True)
    title = models.CharField(max_length=255)
    header_text = models.CharField(max_length=255)
    description_text = models.TextField()
    cause = models.CharField(max_length=100, default="UNKNOWN_CAUSE")
    effect = models.CharField(max_length=100, default="UNKNOWN_EFFECT")
    affected_routes = models.ManyToManyField(
        "routes.Route",
        blank=True,
        related_name="service_alerts",
    )
    is_active = models.BooleanField(default=True, db_index=True)
    active_period_start = models.DateTimeField(null=True, blank=True)
    active_period_end = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "service_alerts"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({'Active' if self.is_active else 'Inactive'})"
