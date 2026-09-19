"""
UniTransit - Position Ingestion Worker
Consumes normalized transport events from Redis Streams, updates vehicle real-time states,
persists positions into PostgreSQL/PostGIS, and broadcasts updates to Redis Pub/Sub.
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

# Setup environment & Django integration
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
try:
    import django
    django.setup()
    from apps.vehicles.models import Vehicle, TransportMode
    from apps.tracking.models import VehiclePosition, TransportEvent
    from apps.routes.models import Route
    from common.metrics import (
        ACTIVE_VEHICLES_GAUGE,
        PROCESSING_LATENCY_HISTOGRAM,
        TELEMETRY_EVENTS_PROCESSED,
    )
except Exception as e:
    # Allows headless testing
    Vehicle = None

from workers.common.redis_client import (
    CHANNEL_VEHICLE_UPDATES,
    CONSUMER_GROUP,
    STREAM_KEY,
    ensure_consumer_group,
    get_redis_client,
    publish_to_channel,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (PositionWorker) %(message)s",
)
logger = logging.getLogger("unitransit.position_worker")


def process_telemetry_event(payload: Dict[str, Any], redis_client=None) -> Dict[str, Any]:
    """
    Processes a single normalized transport event:
    1. Updates or creates Vehicle in persistent storage
    2. Records VehiclePosition time-series
    3. Broadcasts real-time coordinate update via Redis Pub/Sub
    """
    start_time = time.time()
    vehicle_id = payload.get("vehicle_id")
    mode_name = payload.get("mode", "bus")
    route_id = payload.get("route_id")
    lat = float(payload.get("latitude", 0.0))
    lon = float(payload.get("longitude", 0.0))
    speed = float(payload.get("speed", 0.0))
    heading = float(payload.get("heading", 0.0))
    status = payload.get("status", "MOVING")
    occupancy = payload.get("occupancy_status", "MANY_SEATS_AVAILABLE")
    delay = int(payload.get("delay_seconds", 0))
    ts_str = payload.get("timestamp")

    if ts_str:
        try:
            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        except Exception:
            ts = datetime.now(timezone.utc)
    else:
        ts = datetime.now(timezone.utc)

    # 1. Update Persistent Database if Django models are loaded
    if Vehicle is not None:
        try:
            mode_obj, _ = TransportMode.objects.get_or_create(
                name=mode_name,
                defaults={"display_name": mode_name.capitalize(), "icon_name": mode_name},
            )
            route_obj = Route.objects.filter(route_id=route_id).first() if route_id else None

            vehicle_obj, created = Vehicle.objects.get_or_create(
                vehicle_id=vehicle_id,
                defaults={
                    "transport_mode": mode_obj,
                    "current_route": route_obj,
                    "current_latitude": lat,
                    "current_longitude": lon,
                    "current_speed": speed,
                    "current_heading": heading,
                    "status": status,
                    "occupancy_status": occupancy,
                    "delay_seconds": delay,
                    "last_seen": ts,
                },
            )

            if not created:
                vehicle_obj.current_latitude = lat
                vehicle_obj.current_longitude = lon
                vehicle_obj.current_speed = speed
                vehicle_obj.current_heading = heading
                vehicle_obj.status = status
                vehicle_obj.occupancy_status = occupancy
                vehicle_obj.delay_seconds = delay
                vehicle_obj.last_seen = ts
                if route_obj:
                    vehicle_obj.current_route = route_obj
                vehicle_obj.save(
                    update_fields=[
                        "current_latitude",
                        "current_longitude",
                        "current_speed",
                        "current_heading",
                        "status",
                        "occupancy_status",
                        "delay_seconds",
                        "last_seen",
                        "current_route",
                        "updated_at",
                    ]
                )

            # Persist historical timeseries point
            VehiclePosition.objects.create(
                vehicle=vehicle_obj,
                latitude=lat,
                longitude=lon,
                speed=speed,
                heading=heading,
                status=status,
                occupancy_status=occupancy,
                delay_seconds=delay,
                timestamp=ts,
            )

            # Record event audit log
            TransportEvent.objects.create(
                vehicle_id=vehicle_id,
                mode=mode_name,
                route_id=route_id or "",
                payload=payload,
            )

            TELEMETRY_EVENTS_PROCESSED.labels(mode=mode_name, status=status).inc()
        except Exception as db_err:
            logger.error(f"Database persistence error for {vehicle_id}: {db_err}")

    # 2. Real-time Pub/Sub Broadcast (Hot Path)
    broadcast_data = {
        "type": "vehicle.update",
        "vehicle_id": vehicle_id,
        "mode": mode_name,
        "route_id": route_id,
        "latitude": lat,
        "longitude": lon,
        "speed": speed,
        "heading": heading,
        "status": status,
        "occupancy_status": occupancy,
        "delay_seconds": delay,
        "timestamp": ts.isoformat(),
    }

    if redis_client:
        publish_to_channel(redis_client, CHANNEL_VEHICLE_UPDATES, broadcast_data)

    latency = time.time() - start_time
    try:
        PROCESSING_LATENCY_HISTOGRAM.observe(latency)
    except Exception:
        pass

    return broadcast_data


class PositionWorker:
    def __init__(self, consumer_name: str = "pos_worker_1"):
        self.consumer_name = consumer_name
        self.redis_client = None

    def start(self, max_batches: Optional[int] = None):
        logger.info(f"Starting PositionWorker: {self.consumer_name}")
        self.redis_client = get_redis_client()
        ensure_consumer_group(self.redis_client, STREAM_KEY, CONSUMER_GROUP)

        batch_count = 0
        while True:
            try:
                # Read from Redis Stream with consumer group
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
                                process_telemetry_event(payload, self.redis_client)

                            # Acknowledge processed message
                            self.redis_client.xack(STREAM_KEY, CONSUMER_GROUP, msg_id)

                batch_count += 1
                if max_batches and batch_count >= max_batches:
                    logger.info(f"Reached max batch limit of {max_batches}. Exiting worker.")
                    break

            except Exception as e:
                logger.error(f"PositionWorker loop exception: {e}")
                time.sleep(1.0)


if __name__ == "__main__":
    worker = PositionWorker()
    worker.start()
