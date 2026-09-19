"""
UniTransit - Analytics Aggregation Worker
Aggregates route performance, average delays, and fleet statistics.
"""

from __future__ import annotations

import logging
import os
import sys
import time
from datetime import datetime, timezone
from django.db.models import Avg, Count, Max, Min

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
try:
    import django
    django.setup()
    from apps.vehicles.models import Vehicle, TransportMode
    from apps.routes.models import Route
    from apps.analytics.models import DelayAnalytics, FleetStats
    from apps.tracking.models import VehiclePosition
except Exception:
    Vehicle = None

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (AnalyticsWorker) %(message)s",
)
logger = logging.getLogger("unitransit.analytics_worker")


def compute_fleet_statistics():
    """Computes instant snapshot of fleet statistics per transport modality."""
    if Vehicle is None:
        return []
    snapshots = []
    for mode in TransportMode.objects.all():
        vehs = Vehicle.objects.filter(transport_mode=mode)
        total = vehs.count()
        active = vehs.filter(status="MOVING").count()
        delayed = vehs.filter(delay_seconds__gt=120).count()
        avg_spd = vehs.aggregate(Avg("current_speed"))["current_speed__avg"] or 0.0

        stat, _ = FleetStats.objects.update_or_create(
            transport_mode=mode,
            defaults={
                "total_vehicles": total,
                "active_vehicles": active,
                "delayed_vehicles": delayed,
                "average_speed_kmh": round(avg_spd, 1),
            },
        )
        snapshots.append(stat)
    return snapshots


def compute_route_delay_analytics():
    """Aggregates delay stats per route for today."""
    if Vehicle is None:
        return []
    today = datetime.now(timezone.utc).date()
    records = []
    for route in Route.objects.all():
        vehs = route.active_vehicles.all()
        if vehs.exists():
            avg_del = vehs.aggregate(Avg("delay_seconds"))["delay_seconds__avg"] or 0
            max_del = vehs.aggregate(Max("delay_seconds"))["delay_seconds__max"] or 0
            min_del = vehs.aggregate(Min("delay_seconds"))["delay_seconds__min"] or 0
            count = vehs.count()
            on_time = (vehs.filter(delay_seconds__lte=60).count() / max(1, count)) * 100.0

            obj, _ = DelayAnalytics.objects.update_or_create(
                route=route,
                date=today,
                defaults={
                    "avg_delay_seconds": round(avg_del, 1),
                    "max_delay_seconds": int(max_del),
                    "min_delay_seconds": int(min_del),
                    "sample_count": count,
                    "on_time_percentage": round(on_time, 1),
                },
            )
            records.append(obj)
    return records


class AnalyticsWorker:
    def run_once(self):
        stats = compute_fleet_statistics()
        delays = compute_route_delay_analytics()
        logger.info(f"Analytics updated: {len(stats)} fleet modes, {len(delays)} route delay records.")

    def start(self, interval_sec: float = 30.0):
        logger.info(f"Starting AnalyticsWorker (interval={interval_sec}s)...")
        while True:
            try:
                self.run_once()
                time.sleep(interval_sec)
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"AnalyticsWorker error: {e}")
                time.sleep(5.0)


if __name__ == "__main__":
    AnalyticsWorker().start()
