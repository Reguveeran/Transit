import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from datetime import time
from django.test import TestCase
from rest_framework.test import APIClient
from apps.vehicles.models import TransportMode, Vehicle
from apps.routes.models import Route
from apps.stops.models import Stop
from apps.trips.models import Trip, StopTime


class UniTransitAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.mode, _ = TransportMode.objects.get_or_create(
            name="bus",
            defaults={"display_name": "City Bus", "icon_name": "bus"},
        )
        self.route, _ = Route.objects.get_or_create(
            route_id="R-API-101",
            defaults={
                "transport_mode": self.mode,
                "short_name": "R101",
                "long_name": "Express Route",
                "polyline_geojson": {"type": "LineString", "coordinates": [[80.24, 12.97], [80.25, 12.98]]},
            },
        )
        self.vehicle, _ = Vehicle.objects.get_or_create(
            vehicle_id="BUS-API-01",
            defaults={
                "transport_mode": self.mode,
                "current_route": self.route,
                "current_latitude": 12.9716,
                "current_longitude": 80.2440,
                "current_speed": 40.0,
                "current_heading": 90.0,
                "status": "MOVING",
            },
        )
        self.stop, _ = Stop.objects.get_or_create(
            stop_id="STOP-API-01",
            defaults={
                "name": "Central Station",
                "latitude": 12.9716,
                "longitude": 80.2440,
                "transport_mode": self.mode,
            },
        )
        self.trip, _ = Trip.objects.get_or_create(
            trip_id="TRIP-API-01",
            defaults={
                "route": self.route,
                "vehicle": self.vehicle,
                "headsign": "City Center",
            },
        )
        StopTime.objects.get_or_create(
            trip=self.trip,
            stop_sequence=1,
            defaults={
                "stop": self.stop,
                "arrival_time": time(8, 30, 0),
                "departure_time": time(8, 32, 0),
            },
        )

    def test_health_and_ready_probes(self):
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "healthy")

        resp_ready = self.client.get("/ready")
        self.assertEqual(resp_ready.status_code, 200)
        self.assertEqual(resp_ready.json()["status"], "ready")

    def test_prometheus_metrics_endpoint(self):
        resp = self.client.get("/metrics")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"unitransit_api_requests_total", resp.content)

    def test_get_vehicles_list_and_detail(self):
        resp = self.client.get("/api/v1/vehicles/")
        self.assertEqual(resp.status_code, 200)
        results = resp.json().get("results", resp.json())
        self.assertGreaterEqual(len(results), 1)

        detail_resp = self.client.get(f"/api/v1/vehicles/{self.vehicle.vehicle_id}/")
        self.assertEqual(detail_resp.status_code, 200)
        self.assertEqual(detail_resp.json()["vehicle_id"], self.vehicle.vehicle_id)

    def test_get_vehicle_location(self):
        resp = self.client.get(f"/api/v1/vehicles/{self.vehicle.vehicle_id}/location/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["vehicle_id"], self.vehicle.vehicle_id)
        self.assertEqual(data["current_latitude"], 12.9716)
        self.assertEqual(data["current_speed"], 40.0)

    def test_get_routes_and_route_vehicles(self):
        resp = self.client.get("/api/v1/routes/")
        self.assertEqual(resp.status_code, 200)

        detail_resp = self.client.get(f"/api/v1/routes/{self.route.route_id}/")
        self.assertEqual(detail_resp.status_code, 200)
        self.assertEqual(detail_resp.json()["short_name"], "R101")

        veh_resp = self.client.get(f"/api/v1/routes/{self.route.route_id}/vehicles/")
        self.assertEqual(veh_resp.status_code, 200)
        self.assertEqual(len(veh_resp.json()), 1)
        self.assertEqual(veh_resp.json()[0]["vehicle_id"], self.vehicle.vehicle_id)

    def test_get_stops_and_arrivals(self):
        resp = self.client.get("/api/v1/stops/")
        self.assertEqual(resp.status_code, 200)

        detail_resp = self.client.get(f"/api/v1/stops/{self.stop.stop_id}/")
        self.assertEqual(detail_resp.status_code, 200)
        self.assertEqual(detail_resp.json()["name"], "Central Station")

        arrivals_resp = self.client.get(f"/api/v1/stops/{self.stop.stop_id}/arrivals/")
        self.assertEqual(arrivals_resp.status_code, 200)
        self.assertEqual(len(arrivals_resp.json()), 1)
        self.assertEqual(arrivals_resp.json()[0]["trip_id"], self.trip.trip_id)

    def test_get_trips_list_and_detail(self):
        resp = self.client.get("/api/v1/trips/")
        self.assertEqual(resp.status_code, 200)

        detail_resp = self.client.get(f"/api/v1/trips/{self.trip.trip_id}/")
        self.assertEqual(detail_resp.status_code, 200)
        self.assertEqual(detail_resp.json()["headsign"], "City Center")

    def test_get_analytics_endpoints(self):
        veh_analytics = self.client.get("/api/v1/analytics/vehicles/")
        self.assertEqual(veh_analytics.status_code, 200)
        self.assertIn("summary", veh_analytics.json())

        delay_analytics = self.client.get("/api/v1/analytics/delays/")
        self.assertEqual(delay_analytics.status_code, 200)
