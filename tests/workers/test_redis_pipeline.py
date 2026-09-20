import json
import os
import unittest
from unittest.mock import MagicMock, patch

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.test import TestCase, Client
from channels.testing import WebsocketCommunicator
from core.asgi import application
from adapters.common.event_schema import NormalizedTransportEvent, SchemaValidationError
from adapters.simulator.simulator import TransportSimulator
from apps.vehicles.models import Vehicle, TransportMode
from apps.tracking.models import VehiclePosition, TransportEvent
from workers.position_worker.position_worker import PositionWorker, process_telemetry_event


class RedisStreamPipelineTests(TestCase):
    def setUp(self):
        self.mode, _ = TransportMode.objects.get_or_create(
            name="bus",
            defaults={"display_name": "Bus", "icon_name": "bus"},
        )
        self.client = Client()

    # 1. Canonical event validation
    def test_canonical_event_validation_success(self):
        event = NormalizedTransportEvent(
            vehicle_id="BUS-101",
            mode="bus",
            route_id="ROUTE-12",
            latitude=12.9716,
            longitude=80.2440,
            speed=42.5,
            heading=180.0,
            status="MOVING",
            timestamp="2026-09-19T18:30:00Z",
        )
        data = event.to_dict()
        self.assertEqual(data["event_type"], "transport.position.updated")
        self.assertEqual(data["schema_version"], "1.0")
        self.assertEqual(data["vehicle_id"], "BUS-101")
        self.assertEqual(data["latitude"], 12.9716)

    def test_canonical_event_validation_failure(self):
        # Empty vehicle_id
        with self.assertRaises(SchemaValidationError):
            NormalizedTransportEvent(
                vehicle_id="",
                mode="bus",
                route_id="ROUTE-12",
                latitude=12.9716,
                longitude=80.2440,
                speed=42.5,
                heading=180.0,
                status="MOVING",
                timestamp="2026-09-19T18:30:00Z",
            )

        # Latitude out of bounds
        with self.assertRaises(SchemaValidationError):
            NormalizedTransportEvent(
                vehicle_id="BUS-101",
                mode="bus",
                route_id="ROUTE-12",
                latitude=95.0,
                longitude=80.2440,
                speed=42.5,
                heading=180.0,
                status="MOVING",
                timestamp="2026-09-19T18:30:00Z",
            )

    # 2. Simulator publishes to Redis Stream
    def test_simulator_publishes_to_redis_stream(self):
        mock_redis = MagicMock()
        mock_redis.xadd.return_value = "1726770000000-0"

        sim = TransportSimulator(vehicle_count=2, dry_run=False)
        sim.redis_client = mock_redis

        event = NormalizedTransportEvent(
            vehicle_id="BUS-SIM-1",
            mode="bus",
            route_id="ROUTE-12",
            latitude=12.98,
            longitude=80.25,
            speed=35.0,
            heading=90.0,
            status="MOVING",
            timestamp="2026-09-19T18:30:00Z",
        )

        msg_id = sim.publish_event(event)
        self.assertEqual(msg_id, "1726770000000-0")
        mock_redis.xadd.assert_called_once()
        args, kwargs = mock_redis.xadd.call_args
        self.assertEqual(args[0], "transport.events")
        self.assertIn("event", args[1])
        payload = json.loads(args[1]["event"])
        self.assertEqual(payload["vehicle_id"], "BUS-SIM-1")

    # 3 & 4. Worker consumes an event and persists position
    def test_worker_persists_vehicle_and_position(self):
        payload = {
            "event_type": "transport.position.updated",
            "schema_version": "1.0",
            "vehicle_id": "BUS-TEST-01",
            "mode": "bus",
            "route_id": "ROUTE-12",
            "latitude": 12.9750,
            "longitude": 80.2460,
            "speed": 38.0,
            "heading": 120.0,
            "status": "MOVING",
            "occupancy_status": "MANY_SEATS_AVAILABLE",
            "delay_seconds": 10,
            "timestamp": "2026-09-19T18:35:00Z",
        }

        mock_redis = MagicMock()
        broadcast = process_telemetry_event(payload, redis_client=mock_redis)

        self.assertEqual(broadcast["vehicle_id"], "BUS-TEST-01")
        self.assertEqual(broadcast["latitude"], 12.9750)

        # Verify Vehicle is created/updated in DB
        veh = Vehicle.objects.get(vehicle_id="BUS-TEST-01")
        self.assertEqual(veh.current_speed, 38.0)
        self.assertEqual(veh.current_latitude, 12.9750)
        self.assertEqual(veh.status, "MOVING")

        # Verify historical position record
        positions = VehiclePosition.objects.filter(vehicle=veh)
        self.assertEqual(positions.count(), 1)
        self.assertEqual(positions.first().latitude, 12.9750)

        # Verify transport event audit log
        events = TransportEvent.objects.filter(vehicle_id="BUS-TEST-01")
        self.assertEqual(events.count(), 1)

    # 5. Worker publishes vehicle.updates
    def test_worker_publishes_vehicle_updates_channel(self):
        mock_redis = MagicMock()
        payload = {
            "vehicle_id": "BUS-PUB-01",
            "mode": "bus",
            "route_id": "ROUTE-12",
            "latitude": 12.9800,
            "longitude": 80.2480,
            "speed": 40.0,
            "heading": 150.0,
            "status": "MOVING",
            "timestamp": "2026-09-19T18:36:00Z",
        }

        process_telemetry_event(payload, redis_client=mock_redis)

        # Verify publish called on channel "vehicle.updates"
        mock_redis.publish.assert_called_once()
        call_args = mock_redis.publish.call_args[0]
        self.assertEqual(call_args[0], "vehicle.updates")
        published_data = json.loads(call_args[1])
        self.assertEqual(published_data["vehicle_id"], "BUS-PUB-01")
        self.assertEqual(published_data["latitude"], 12.9800)

    # 6. Successful event is XACKed
    def test_successful_event_is_xacked(self):
        mock_redis = MagicMock()
        worker = PositionWorker(consumer_name="test_worker")
        worker.redis_client = mock_redis

        payload = {
            "vehicle_id": "BUS-XACK-01",
            "mode": "bus",
            "route_id": "ROUTE-12",
            "latitude": 12.9810,
            "longitude": 80.2490,
            "speed": 30.0,
            "heading": 180.0,
            "status": "MOVING",
            "timestamp": "2026-09-19T18:37:00Z",
        }

        msg_id = "1726771000000-0"
        data = {"event": json.dumps(payload)}

        worker._process_single_message(msg_id, data)

        mock_redis.xack.assert_called_once_with("transport.events", "unitransit_workers", msg_id)

    # 7. Failed event (database error) is NOT incorrectly acknowledged
    def test_failed_event_is_not_xacked(self):
        mock_redis = MagicMock()
        worker = PositionWorker(consumer_name="test_worker")
        worker.redis_client = mock_redis

        payload = {
            "vehicle_id": "BUS-FAIL-01",
            "mode": "bus",
            "route_id": "ROUTE-12",
            "latitude": 12.9810,
            "longitude": 80.2490,
            "speed": 30.0,
            "heading": 180.0,
            "status": "MOVING",
            "timestamp": "2026-09-19T18:37:00Z",
        }

        msg_id = "1726772000000-0"
        data = {"event": json.dumps(payload)}

        # Simulate database failure during processing
        with patch("apps.vehicles.models.Vehicle.objects.get_or_create", side_effect=Exception("DB Connection Dropped")):
            worker._process_single_message(msg_id, data)

        # Must NOT call XACK on infrastructure failure
        mock_redis.xack.assert_not_called()

    # 8. WebSocket receives update
    async def test_websocket_receives_update(self):
        communicator = WebsocketCommunicator(application, "/ws/vehicles/")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            "vehicle_updates",
            {
                "type": "vehicle.update",
                "data": {
                    "event_type": "vehicle.position.updated",
                    "vehicle_id": "BUS-WS-LIVE",
                    "mode": "bus",
                    "latitude": 12.9880,
                    "longitude": 80.2530,
                    "speed": 48.0,
                },
            },
        )

        response = await communicator.receive_from()
        msg = json.loads(response)
        self.assertEqual(msg["vehicle_id"], "BUS-WS-LIVE")
        self.assertEqual(msg["latitude"], 12.9880)

        await communicator.disconnect()

    # 9. Malformed event is rejected and isolated (poison pill XACKed)
    def test_malformed_event_isolated(self):
        mock_redis = MagicMock()
        worker = PositionWorker(consumer_name="test_worker")
        worker.redis_client = mock_redis

        # Corrupt data: latitude is not a number
        malformed_payload = {
            "vehicle_id": "BUS-BAD-01",
            "mode": "bus",
            "route_id": "ROUTE-12",
            "latitude": "NOT_A_COORDINATE",
            "longitude": 80.2490,
            "speed": 30.0,
            "heading": 180.0,
            "status": "MOVING",
            "timestamp": "2026-09-19T18:37:00Z",
        }

        msg_id = "1726773000000-0"
        data = {"event": json.dumps(malformed_payload)}

        worker._process_single_message(msg_id, data)

        # Poison pill must be XACKed so queue is not blocked
        mock_redis.xack.assert_called_once_with("transport.events", "unitransit_workers", msg_id)

    # 10. Readiness check probe handles Redis and DB health
    def test_readiness_probe_healthy(self):
        with patch("redis.Redis.ping", return_value=True):
            resp = self.client.get("/ready")
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertEqual(data["status"], "ready")
            self.assertEqual(data["database"], "connected")
            self.assertEqual(data["redis"], "connected")

    def test_readiness_probe_unhealthy_when_redis_down(self):
        with patch("redis.Redis.ping", side_effect=Exception("Redis Connection Refused")):
            resp = self.client.get("/ready")
            self.assertEqual(resp.status_code, 503)
            data = resp.json()
            self.assertEqual(data["status"], "unready")
            self.assertIn("error", data["redis"])
