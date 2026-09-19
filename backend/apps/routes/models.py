from django.db import models


class Route(models.Model):
    route_id = models.CharField(max_length=64, unique=True, db_index=True)
    transport_mode = models.ForeignKey(
        "vehicles.TransportMode",
        on_delete=models.PROTECT,
        related_name="routes",
    )
    short_name = models.CharField(max_length=30)  # e.g. "R12", "BLUE"
    long_name = models.CharField(max_length=255)  # e.g. "Downtown - Airport Express"
    description = models.TextField(blank=True)
    color = models.CharField(max_length=10, default="#2563EB")  # Hex color for map rendering
    text_color = models.CharField(max_length=10, default="#FFFFFF")
    is_active = models.BooleanField(default=True)
    # Stored as GeoJSON LineString coordinates: [[lon, lat], ...]
    polyline_geojson = models.JSONField(
        default=dict,
        blank=True,
        help_text="GeoJSON representation of the route polyline path.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "routes"
        ordering = ["short_name"]

    def __str__(self):
        return f"{self.short_name} - {self.long_name}"
