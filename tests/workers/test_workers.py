import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.test import TestCase
from apps.vehicles.models import Vehicle, TransportMode
from apps.routes.models import Route
from apps.tracking.models import VehiclePosition, TransportEvent
from apps.alerts.models import Alert
from workers.position_worker.position_worker import process_telemetry_event
from workers.alert_worker.alert_worker import evaluate_event_alerts
from workers.analytics_worker.analytics_worker import (
    compute_fleet_statistics,
    compute_route_delay_analytics,
)


class WorkerTests(TestCase):
    def setUp(self):
        self.mode, _ = TransportMode.objects.get_or_create(
            name="bus",
            defaults={"display_name": "City Bus", "icon_name": "bus"},
        )
        self.route, _ = Route.objects.get_or_create(
            route_id="R-WORKER-01",
            defaults={
                "transport_mode": self.mode,
                "short_name": "W1",
                "long_name": "Worker Route",
            },
        )
        self.vehicle, _ = Vehicle.objects.get_or_create(
            vehicle_id="BUS-PW-01",
            defaults={
                "transport_mode": self.mode,
                "current_route": self.route,
                "current_latitude": 12.9850,
                "current_longitude": 80.2520,
            },
        )

    def test_position_worker_telemetry_processing(self):
        payload = {
            "vehicle_id": "BUS-PW-01",
            "mode": "bus",
            "route_id": "R-WORKER-01",
            "latitude": 12.9850,
            "longitude": 80.2520,
            "speed": 44.5,
            "heading": 120.0,
            "status": "MOVING",
            "occupancy_status": "MANY_SEATS_AVAILABLE",
            "delay_seconds": 15,
            "timestamp": "2026-09-19T18:30:00Z",
        }

        # Process event (without requiring active Redis broker)
        broadcast = process_telemetry_event(payload, redis_client=None)

        self.assertEqual(broadcast["vehicle_id"], "BUS-PW-01")
        self.assertEqual(broadcast["latitude"], 12.9850)

        # Verify DB records
        veh = Vehicle.objects.get(vehicle_id="BUS-PW-01")
        self.assertEqual(veh.current_speed, 44.5)
        self.assertEqual(veh.status, "MOVING")

        pos_count = VehiclePosition.objects.filter(vehicle=veh).count()
        self.assertEqual(pos_count, 1)

        event_count = TransportEvent.objects.filter(vehicle_id="BUS-PW-01").count()
        self.assertEqual(event_count, 1)

    def test_alert_worker_overspeed_evaluation(self):
        # Bus speed limit is 75 km/h. Speed 92 km/h must trigger an OVERSPEED alert
        payload = {
            "vehicle_id": "BUS-PW-01",
            "mode": "bus",
            "route_id": "R-WORKER-01",
            "latitude": 12.9850,
            "longitude": 80.2520,
            "speed": 92.0,
            "heading": 120.0,
            "status": "MOVING",
            "delay_seconds": 20,
        }
        alerts = evaluate_event_alerts(payload, redis_client=None)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["alert_type"], "OVERSPEED")
        self.assertIn("exceeded speed limit", alerts[0]["message"])

        # Check DB
        db_alert = Alert.objects.filter(vehicle__vehicle_id="BUS-PW-01", alert_type="OVERSPEED").first()
        self.assertIsNotNone(db_alert)

    def test_alert_worker_long_delay_evaluation(self):
        # Delay > 300 seconds must trigger LONG_DELAY alert
        payload = {
            "vehicle_id": "BUS-PW-01",
            "mode": "bus",
            "route_id": "R-WORKER-01",
            "latitude": 12.9850,
            "longitude": 80.2520,
            "speed": 30.0,
            "heading": 120.0,
            "status": "MOVING",
            "delay_seconds": 450,
        }
        alerts = evaluate_event_alerts(payload, redis_client=None)
        self.assertTrue(any(a["alert_type"] == "LONG_DELAY" for a in alerts))

    def test_analytics_worker_computation(self):
        # Create a moving vehicle on route
        Vehicle.objects.create(
            vehicle_id="BUS-AN-01",
            transport_mode=self.mode,
            current_route=self.route,
            current_latitude=12.98,
            current_longitude=80.25,
            current_speed=30.0,
            status="MOVING",
            delay_seconds=40,
        )

        stats = compute_fleet_statistics()
        self.assertGreaterEqual(len(stats), 1)

        delays = compute_route_delay_analytics()
        self.assertGreaterEqual(len(delays), 1)
