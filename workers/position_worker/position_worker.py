"""
UniTransit - Real Redis Stream Position Ingestion Worker
Consumes canonical transport events (transport.event.v1) from Redis Stream `transport.events`
using consumer group `unitransit_workers`. Persists vehicle state and spatial timeseries to
PostgreSQL/PostGIS, and broadcasts updates via Redis Pub/Sub and Django Channels.
"""

from __future__ import annotations

import json
import logging
import os
import signal
import sys
import time
import uuid
from datetime import datetime, timedelta, timezone
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
        EVENTS_PROCESSED_TOTAL,
        EVENTS_FAILED_TOTAL,
        PROCESSING_LATENCY_SECONDS,
        WORKER_UP,
        STREAM_CONSUMER_LAG,
    )
except Exception as e:
    Vehicle = None
    ACTIVE_VEHICLES_GAUGE = None
    EVENTS_PROCESSED_TOTAL = None
    EVENTS_FAILED_TOTAL = None
    PROCESSING_LATENCY_SECONDS = None
    WORKER_UP = None
    STREAM_CONSUMER_LAG = None

from adapters.common.event_schema import (
    NormalizedTransportEvent,
    SchemaValidationError,
)
from workers.common.redis_client import (
    CHANNEL_VEHICLE_UPDATES,
    CONSUMER_GROUP,
    STREAM_KEY,
    ensure_consumer_group,
    get_redis_client,
    publish_to_channel,
)

# Configure base logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (PositionWorker) %(message)s",
)
logger = logging.getLogger("unitransit.position_worker")


def log_structured(level: str, event_type: str, **kwargs) -> None:
    """Emits JSON formatted structured operational logs to stdout."""
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": level.upper(),
        "service": "position-worker",
        "event": event_type,
    }
    payload.update(kwargs)
    print(json.dumps(payload), flush=True)


def process_telemetry_event(payload: Dict[str, Any], redis_client=None) -> Dict[str, Any]:
    """
    Validates, normalizes, persists, and broadcasts a single canonical transport event:
    1. Validates strictly against canonical transport.event.v1 specification
    2. Updates or creates Vehicle latest state in persistent storage
    3. Records VehiclePosition historical timeseries point
    4. Records TransportEvent audit log
    5. Dispatches real-time update via Redis Pub/Sub and Django Channels
    """
    start_time = time.time()

    # 1. Canonical Schema Validation
    try:
        norm_event = NormalizedTransportEvent.from_dict(payload)
    except (SchemaValidationError, ValueError, TypeError) as val_err:
        log_structured("WARN", "malformed_event_rejected", error=str(val_err), payload=payload)
        if EVENTS_FAILED_TOTAL:
            EVENTS_FAILED_TOTAL.labels(reason="schema_validation", service="position-worker").inc()
        raise val_err

    vehicle_id = norm_event.vehicle_id
    mode_name = str(norm_event.mode.value if hasattr(norm_event.mode, "value") else norm_event.mode).lower()
    route_id = norm_event.route_id
    lat = norm_event.latitude
    lon = norm_event.longitude
    speed = norm_event.speed
    heading = norm_event.heading
    status = str(norm_event.status.value if hasattr(norm_event.status, "value") else norm_event.status).upper()
    occupancy = str(
        norm_event.occupancy_status.value
        if hasattr(norm_event.occupancy_status, "value")
        else norm_event.occupancy_status or "MANY_SEATS_AVAILABLE"
    )
    delay = norm_event.delay_seconds

    try:
        ts = datetime.fromisoformat(norm_event.timestamp.replace("Z", "+00:00"))
    except Exception:
        ts = datetime.now(timezone.utc)

    # 2. Update Persistent Database (PostgreSQL / SQLite)
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

            if EVENTS_PROCESSED_TOTAL:
                EVENTS_PROCESSED_TOTAL.labels(mode=mode_name, status=status).inc()

        except Exception as db_err:
            log_structured("ERROR", "database_persistence_failed", vehicle_id=vehicle_id, error=str(db_err))
            if EVENTS_FAILED_TOTAL:
                EVENTS_FAILED_TOTAL.labels(reason="database_error", service="position-worker").inc()
            raise db_err

    # 3. Real-time Pub/Sub Broadcast (Published strictly after successful persistence)
    broadcast_data = {
        "event_type": "vehicle.position.updated",
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

    # Broadcast to Redis Pub/Sub channel
    if redis_client:
        publish_to_channel(redis_client, CHANNEL_VEHICLE_UPDATES, broadcast_data)

    # Broadcast directly to Django Channels group `vehicle_updates`
    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        ch_layer = get_channel_layer()
        if ch_layer:
            async_to_sync(ch_layer.group_send)(
                "vehicle_updates",
                {
                    "type": "vehicle.update",
                    "data": broadcast_data,
                },
            )
    except Exception as ch_err:
        logger.debug(f"Django channel layer broadcast notice: {ch_err}")

    # Latency tracking
    latency_ms = round((time.time() - start_time) * 1000, 2)
    if PROCESSING_LATENCY_SECONDS:
        try:
            PROCESSING_LATENCY_SECONDS.observe(latency_ms / 1000.0)
        except Exception:
            pass

    log_structured(
        "INFO",
        "vehicle_position_processed",
        vehicle_id=vehicle_id,
        mode=mode_name,
        stream=STREAM_KEY,
        latency_ms=latency_ms,
    )

    return broadcast_data


class PositionWorker:
    """
    Long-running Redis Stream Consumer with consumer group fault-tolerance,
    retention pruning, and structured observability.
    """

    def __init__(self, consumer_name: Optional[str] = None):
        self.consumer_name = consumer_name or f"position-worker-{uuid.uuid4().hex[:8]}"
        self.redis_client = None
        self.running = True
        self._last_prune = time.time()
        self._setup_signals()

    def _setup_signals(self):
        def _shutdown_handler(signum, frame):
            sig_name = "SIGTERM" if signum == signal.SIGTERM else "SIGINT"
            log_structured("INFO", "worker_signal_received", signal=sig_name, consumer=self.consumer_name)
            self.running = False

        signal.signal(signal.SIGINT, _shutdown_handler)
        signal.signal(signal.SIGTERM, _shutdown_handler)

    def prune_old_positions(self, retention_hours: int = 24):
        """Removes historical positions older than retention threshold to prevent unbounded growth."""
        if VehiclePosition is None:
            return
        try:
            threshold = datetime.now(timezone.utc) - timedelta(hours=retention_hours)
            deleted, _ = VehiclePosition.objects.filter(timestamp__lt=threshold).delete()
            if deleted > 0:
                log_structured("INFO", "positions_retention_pruned", deleted_count=deleted, threshold=threshold.isoformat())
        except Exception as e:
            log_structured("WARN", "retention_pruning_error", error=str(e))

    def recover_pending_messages(self):
        """Attempts to claim and process stalled messages left by ungracefully terminated consumers."""
        if not self.redis_client:
            return
        try:
            # xautoclaim claims messages pending > 30,000ms
            claimed = self.redis_client.xautoclaim(
                STREAM_KEY,
                CONSUMER_GROUP,
                self.consumer_name,
                min_idle_time=30000,
                start_id="0-0",
                count=25,
            )
            if claimed and len(claimed) > 1 and claimed[1]:
                messages = claimed[1]
                log_structured("INFO", "recovering_pending_messages", count=len(messages))
                for msg_id, data in messages:
                    self._process_single_message(msg_id, data)
        except Exception as e:
            # Older Redis servers or empty stream
            pass

    def _process_single_message(self, msg_id: str, data: Dict[str, Any]):
        event_raw = data.get("event")
        if not event_raw:
            self.redis_client.xack(STREAM_KEY, CONSUMER_GROUP, msg_id)
            return

        payload = json.loads(event_raw) if isinstance(event_raw, str) else event_raw

        try:
            process_telemetry_event(payload, self.redis_client)
            # Acknowledge on successful validation, persistence, and dispatch
            self.redis_client.xack(STREAM_KEY, CONSUMER_GROUP, msg_id)
        except (SchemaValidationError, ValueError, TypeError) as val_err:
            # Poison pill isolation: acknowledge so malformed event does not lock stream
            self.redis_client.xack(STREAM_KEY, CONSUMER_GROUP, msg_id)
            log_structured("WARN", "poison_pill_isolated", msg_id=msg_id, error=str(val_err))
        except Exception as proc_err:
            # Infrastructure failure: do NOT XACK so it will be retried
            log_structured("ERROR", "message_processing_failed", msg_id=msg_id, error=str(proc_err))

    def start(self, max_batches: Optional[int] = None):
        log_structured("INFO", "worker_starting", consumer=self.consumer_name, stream=STREAM_KEY, group=CONSUMER_GROUP)

        try:
            self.redis_client = get_redis_client()
            self.redis_client.ping()
        except Exception as conn_err:
            log_structured("ERROR", "redis_connection_failed", error=str(conn_err))
            raise conn_err

        # Ensure stream & group exist idempotently
        ensure_consumer_group(self.redis_client, STREAM_KEY, CONSUMER_GROUP)

        if WORKER_UP:
            WORKER_UP.labels(worker_type="position-worker", consumer_id=self.consumer_name).set(1)

        batch_count = 0
        last_lag_sample = time.time()

        try:
            while self.running:
                # 1. Periodically update consumer stream lag metric
                now = time.time()
                if now - last_lag_sample >= 5.0 and STREAM_CONSUMER_LAG:
                    try:
                        pending_info = self.redis_client.xpending(STREAM_KEY, CONSUMER_GROUP)
                        lag = pending_info.get("pending", 0) if isinstance(pending_info, dict) else 0
                        STREAM_CONSUMER_LAG.labels(stream=STREAM_KEY, group=CONSUMER_GROUP).set(lag)
                    except Exception:
                        pass
                    last_lag_sample = now

                # 2. Periodically prune old positions
                if now - self._last_prune >= 300:
                    self.prune_old_positions(retention_hours=24)
                    self.recover_pending_messages()
                    self._last_prune = now

                # 3. Read batch from Redis Stream via consumer group
                try:
                    response = self.redis_client.xreadgroup(
                        groupname=CONSUMER_GROUP,
                        consumername=self.consumer_name,
                        streams={STREAM_KEY: ">"},
                        count=50,
                        block=1000,
                    )

                    if response:
                        for stream_name, messages in response:
                            for msg_id, data in messages:
                                self._process_single_message(msg_id, data)

                    batch_count += 1
                    if max_batches and batch_count >= max_batches:
                        log_structured("INFO", "worker_max_batches_reached", batches=batch_count)
                        break

                except Exception as read_err:
                    if not self.running:
                        break
                    log_structured("ERROR", "stream_read_error", error=str(read_err))
                    time.sleep(1.0)

        finally:
            log_structured("INFO", "worker_stopped_gracefully", consumer=self.consumer_name)
            if WORKER_UP:
                WORKER_UP.labels(worker_type="position-worker", consumer_id=self.consumer_name).set(0)
            if self.redis_client:
                try:
                    self.redis_client.close()
                except Exception:
                    pass


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="UniTransit Position Worker")
    parser.add_argument("--consumer-name", type=str, default=None, help="Unique worker consumer name")
    parser.add_argument("--metrics-port", type=int, default=int(os.getenv("WORKER_METRICS_PORT", "9102")), help="Prometheus metrics exporter port")
    parser.add_argument("--no-metrics", action="store_true", help="Disable Prometheus metrics server")
    args = parser.parse_args()

    if not args.no_metrics:
        try:
            from prometheus_client import start_http_server
            start_http_server(args.metrics_port)
            log_structured("INFO", "worker_metrics_server_started", port=args.metrics_port)
        except Exception as met_err:
            logger.debug(f"Metrics server could not bind to port {args.metrics_port}: {met_err}")

    worker = PositionWorker(consumer_name=args.consumer_name)
    worker.start()
