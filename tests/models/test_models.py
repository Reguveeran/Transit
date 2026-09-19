import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from datetime import datetime, timezone, time
from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.vehicles.models import TransportMode, Vehicle
from apps.routes.models import Route
from apps.stops.models import Stop
from apps.trips.models import Trip, StopTime
from apps.tracking.models import VehiclePosition, TransportEvent
from apps.alerts.models import Alert, ServiceAlert
from apps.analytics.models import DelayAnalytics, FleetStats

User = get_user_model()


class UniTransitModelTests(TestCase):
    def setUp(self):
        self.bus_mode, _ = TransportMode.objects.get_or_create(
            name="test_bus",
            defaults={"display_name": "Test Bus", "icon_name": "bus"},
        )
        self.route, _ = Route.objects.get_or_create(
            route_id="R-TEST-UNIQUE-1",
            defaults={
                "transport_mode": self.bus_mode,
                "short_name": "T1",
                "long_name": "Test Route One",
                "polyline_geojson": {"type": "LineString", "coordinates": [[80.24, 12.97], [80.25, 12.98]]},
            },
        )
        self.vehicle, _ = Vehicle.objects.get_or_create(
            vehicle_id="BUS-TEST-UNIQ-01",
            defaults={
                "transport_mode": self.bus_mode,
                "current_route": self.route,
                "current_latitude": 12.9716,
                "current_longitude": 80.2440,
                "current_speed": 35.0,
                "status": "MOVING",
            },
        )
        self.stop1, _ = Stop.objects.get_or_create(
            stop_id="STOP-T1-UNIQ",
            defaults={
                "name": "Test Stop Alpha",
                "latitude": 12.9716,
                "longitude": 80.2440,
                "transport_mode": self.bus_mode,
            },
        )
        self.stop2, _ = Stop.objects.get_or_create(
            stop_id="STOP-T2-UNIQ",
            defaults={
                "name": "Test Stop Beta",
                "latitude": 12.9800,
                "longitude": 80.2480,
                "transport_mode": self.bus_mode,
            },
        )

    def test_custom_user_role(self):
        user = User.objects.create_user(
            username="dispatcher1",
            email="dispatcher1@unitransit.local",
            password="secretpassword123",
            role="DISPATCHER",
        )
        self.assertEqual(user.role, "DISPATCHER")
        self.assertTrue(str(user).startswith("dispatcher1"))

    def test_vehicle_properties(self):
        self.assertTrue(self.vehicle.is_moving)
        self.vehicle.current_speed = 0.0
        self.vehicle.status = "STOPPED"
        self.assertFalse(self.vehicle.is_moving)

    def test_stop_haversine_distance(self):
        # Distance between stop1 (12.9716, 80.2440) and stop2 (12.9800, 80.2480)
        dist_km = self.stop1.distance_to(self.stop2.latitude, self.stop2.longitude)
        self.assertGreater(dist_km, 0.8)
        self.assertLess(dist_km, 1.5)

    def test_trip_and_stop_time_relation(self):
        trip = Trip.objects.create(
            trip_id="TRIP-TEST-001",
            route=self.route,
            vehicle=self.vehicle,
            headsign="North Station",
        )
        st1 = StopTime.objects.create(
            trip=trip,
            stop=self.stop1,
            stop_sequence=1,
            arrival_time=time(9, 0, 0),
            departure_time=time(9, 2, 0),
        )
        st2 = StopTime.objects.create(
            trip=trip,
            stop=self.stop2,
            stop_sequence=2,
            arrival_time=time(9, 15, 0),
            departure_time=time(9, 17, 0),
        )
        self.assertEqual(trip.stop_times.count(), 2)
        self.assertEqual(list(trip.stop_times.values_list("stop_sequence", flat=True)), [1, 2])

    def test_vehicle_position_and_transport_event(self):
        now = datetime.now(timezone.utc)
        pos = VehiclePosition.objects.create(
            vehicle=self.vehicle,
            latitude=12.9720,
            longitude=80.2445,
            speed=36.0,
            heading=90.0,
            status="MOVING",
            timestamp=now,
        )
        self.assertEqual(pos.vehicle.vehicle_id, self.vehicle.vehicle_id)

        event = TransportEvent.objects.create(
            vehicle_id=self.vehicle.vehicle_id,
            mode="bus",
            route_id="R-TEST-1",
            payload={"speed": 36.0, "status": "MOVING"},
        )
        self.assertIsNotNone(event.event_id)
        self.assertEqual(event.payload["speed"], 36.0)

    def test_alerts_and_service_alerts(self):
        alert = Alert.objects.create(
            alert_type="OVERSPEED",
            severity="CRITICAL",
            vehicle=self.vehicle,
            route=self.route,
            message="Speed 85 km/h exceeded limit 50 km/h",
        )
        self.assertFalse(alert.is_resolved)

        service_alert = ServiceAlert.objects.create(
            alert_id="SRV-TEST-01",
            title="Severe Weather Advisory",
            header_text="Storm watch in effect",
            description_text="Reduced transit schedules",
        )
        service_alert.affected_routes.add(self.route)
        self.assertIn(self.route, service_alert.affected_routes.all())

    def test_analytics_records(self):
        today = datetime.now(timezone.utc).date()
        analytics = DelayAnalytics.objects.create(
            route=self.route,
            date=today,
            avg_delay_seconds=42.5,
            max_delay_seconds=120,
            sample_count=100,
        )
        self.assertEqual(analytics.avg_delay_seconds, 42.5)

        stats = FleetStats.objects.create(
            transport_mode=self.bus_mode,
            total_vehicles=20,
            active_vehicles=18,
            delayed_vehicles=2,
            average_speed_kmh=34.2,
        )
        self.assertEqual(stats.active_vehicles, 18)
