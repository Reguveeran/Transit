from django.db import models


class DelayAnalytics(models.Model):
    route = models.ForeignKey(
        "routes.Route",
        on_delete=models.CASCADE,
        related_name="delay_analytics",
    )
    date = models.DateField(db_index=True)
    avg_delay_seconds = models.FloatField(default=0.0)
    max_delay_seconds = models.IntegerField(default=0)
    min_delay_seconds = models.IntegerField(default=0)
    sample_count = models.PositiveIntegerField(default=0)
    on_time_percentage = models.FloatField(default=100.0)
    calculated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "delay_analytics"
        unique_together = ("route", "date")
        ordering = ["-date", "route"]

    def __str__(self):
        return f"{self.route.short_name} on {self.date}: {self.avg_delay_seconds:.1f}s avg delay"


class FleetStats(models.Model):
    transport_mode = models.ForeignKey(
        "vehicles.TransportMode",
        on_delete=models.CASCADE,
        related_name="fleet_stats",
    )
    total_vehicles = models.PositiveIntegerField(default=0)
    active_vehicles = models.PositiveIntegerField(default=0)
    delayed_vehicles = models.PositiveIntegerField(default=0)
    average_speed_kmh = models.FloatField(default=0.0)
    recorded_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "fleet_stats"
        ordering = ["-recorded_at"]

    def __str__(self):
        return f"{self.transport_mode.name} Stats @ {self.recorded_at}: {self.active_vehicles}/{self.total_vehicles} active"
