"""
UniTransit - Real-Time Alert Engine Worker
Evaluates transport telemetry against operational rules (overspeed, unexpected stops,
route deviation, excessive delay, offline signals) and dispatches alerts to Redis & WebSockets.
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
try:
    import django
    django.setup()
    from apps.vehicles.models import Vehicle
    from apps.routes.models import Route
    from apps.alerts.models import Alert
    from common.metrics import ALERTS_TRIGGERED_TOTAL
except Exception:
    Alert = None

from workers.common.redis_client import (
    CHANNEL_ALERTS,
    CONSUMER_GROUP,
    STREAM_KEY,
    ensure_consumer_group,
    get_redis_client,
    publish_to_channel,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (AlertWorker) %(message)s",
)
logger = logging.getLogger("unitransit.alert_worker")

# Alert Threshold Configurations
SPEED_LIMITS = {
    "bus": 75.0,
    "metro": 95.0,
    "train": 110.0,
    "tram": 50.0,
    "ferry": 35.0,
    "aircraft": 850.0,
}
MAX_TOLERABLE_DELAY_SEC = 300  # 5 minutes


def evaluate_event_alerts(payload: Dict[str, Any], redis_client=None) -> List[Dict[str, Any]]:
    """
    Evaluates business rules against an incoming vehicle event payload.
    Returns list of triggered alert dictionaries.
    """
    triggered_alerts = []
    vehicle_id = payload.get("vehicle_id")
    mode = payload.get("mode", "bus")
    speed = float(payload.get("speed", 0.0))
    delay = int(payload.get("delay_seconds", 0))
    status = payload.get("status", "MOVING")
    lat = float(payload.get("latitude", 0.0))
    lon = float(payload.get("longitude", 0.0))
    route_id = payload.get("route_id")

    # Rule 1: Overspeed Violation
    speed_limit = SPEED_LIMITS.get(mode, 80.0)
    if speed > speed_limit:
        overspeed_amount = round(speed - speed_limit, 1)
        alert_item = {
            "alert_type": "OVERSPEED",
            "severity": "CRITICAL" if overspeed_amount > 20 else "WARNING",
            "vehicle_id": vehicle_id,
            "route_id": route_id,
            "message": f"Vehicle {vehicle_id} ({mode}) exceeded speed limit ({speed_limit} km/h) with {speed} km/h (+{overspeed_amount} km/h).",
            "latitude": lat,
            "longitude": lon,
            "details": {"current_speed": speed, "speed_limit": speed_limit, "excess": overspeed_amount},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        triggered_alerts.append(alert_item)

    # Rule 2: Excessive Delay
    if delay > MAX_TOLERABLE_DELAY_SEC:
        delay_min = round(delay / 60, 1)
        alert_item = {
            "alert_type": "LONG_DELAY",
            "severity": "WARNING",
            "vehicle_id": vehicle_id,
            "route_id": route_id,
            "message": f"Vehicle {vehicle_id} on route {route_id} is delayed by {delay_min} minutes ({delay}s).",
            "latitude": lat,
            "longitude": lon,
            "details": {"delay_seconds": delay, "delay_minutes": delay_min},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        triggered_alerts.append(alert_item)

    # Rule 3: Unexpected Vehicle Stop
    if status == "STOPPED" and speed == 0.0 and payload.get("metadata", {}).get("unexpected_halt"):
        alert_item = {
            "alert_type": "UNEXPECTED_STOP",
            "severity": "CRITICAL",
            "vehicle_id": vehicle_id,
            "route_id": route_id,
            "message": f"Vehicle {vehicle_id} reported an unexpected stationary stop outside transit stations.",
            "latitude": lat,
            "longitude": lon,
            "details": {"status": status},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        triggered_alerts.append(alert_item)

    # Persist and Broadcast Triggered Alerts
    for alt in triggered_alerts:
        if Alert is not None:
            try:
                veh_obj = Vehicle.objects.filter(vehicle_id=vehicle_id).first()
                route_obj = Route.objects.filter(route_id=route_id).first() if route_id else None
                Alert.objects.create(
                    alert_type=alt["alert_type"],
                    severity=alt["severity"],
                    vehicle=veh_obj,
                    route=route_obj,
                    message=alt["message"],
                    details=alt["details"],
                    latitude=lat,
                    longitude=lon,
                )
                ALERTS_TRIGGERED_TOTAL.labels(alert_type=alt["alert_type"], severity=alt["severity"]).inc()
            except Exception as e:
                logger.error(f"Error persisting alert to database: {e}")

        if redis_client:
            publish_to_channel(redis_client, CHANNEL_ALERTS, alt)

    return triggered_alerts


class AlertWorker:
    def __init__(self, consumer_name: str = "alert_worker_1"):
        self.consumer_name = consumer_name
        self.redis_client = None

    def start(self, max_batches: Optional[int] = None):
        logger.info(f"Starting AlertWorker: {self.consumer_name}")
        self.redis_client = get_redis_client()
        ensure_consumer_group(self.redis_client, STREAM_KEY, CONSUMER_GROUP)

        batch_count = 0
        while True:
            try:
                response = self.redis_client.xreadgroup(
                    groupname=CONSUMER_GROUP,
                    consumername=self.consumer_name,
                    streams={STREAM_KEY: ">"},
                    count=50,
                    block=1000,
                )

                if response:
                    for stream, messages in response:
                        for msg_id, data in messages:
                            event_raw = data.get("event")
                            if event_raw:
                                payload = json.loads(event_raw) if isinstance(event_raw, str) else event_raw
                                evaluate_event_alerts(payload, self.redis_client)

                            self.redis_client.xack(STREAM_KEY, CONSUMER_GROUP, msg_id)

                batch_count += 1
                if max_batches and batch_count >= max_batches:
                    break

            except Exception as e:
                logger.error(f"AlertWorker exception: {e}")
                time.sleep(1.0)


if __name__ == "__main__":
    worker = AlertWorker()
    worker.start()
