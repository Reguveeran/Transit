import math
from django.db import models


class Stop(models.Model):
    stop_id = models.CharField(max_length=64, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=30, blank=True)
    latitude = models.FloatField(db_index=True)
    longitude = models.FloatField(db_index=True)
    zone_id = models.CharField(max_length=50, blank=True)
    transport_mode = models.ForeignKey(
        "vehicles.TransportMode",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stops",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "stops"
        indexes = [
            models.Index(fields=["latitude", "longitude"]),
        ]
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.stop_id})"

    def distance_to(self, lat: float, lon: float) -> float:
        """Returns great-circle distance in kilometers using Haversine formula."""
        r = 6371.0  # Earth radius in kilometers
        d_lat = math.radians(lat - self.latitude)
        d_lon = math.radians(lon - self.longitude)
        a = (
            math.sin(d_lat / 2) ** 2
            + math.cos(math.radians(self.latitude))
            * math.cos(math.radians(lat))
            * math.sin(d_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return r * c
