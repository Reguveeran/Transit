from django.test import TestCase
from rest_framework.test import APIClient
from apps.vehicles.models import TransportMode, Vehicle
from apps.routes.models import Route
from apps.stops.models import Stop


class DevOpsAndCommuterAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.mode, _ = TransportMode.objects.get_or_create(
            name="bus",
            defaults={"display_name": "City Bus", "icon_name": "bus"}
        )
        self.route, _ = Route.objects.get_or_create(
            route_id="R-TEST",
            defaults={
                "transport_mode": self.mode,
                "short_name": "RT",
                "long_name": "Test Corridor",
                "polyline_geojson": {
                    "type": "LineString",
                    "coordinates": [[80.24, 12.99], [80.25, 12.995], [80.26, 13.00]]
                }
            }
        )
        self.stop, _ = Stop.objects.get_or_create(
            stop_id="ST-TEST",
            defaults={
                "name": "Test Station",
                "code": "TST",
                "latitude": 12.991,
                "longitude": 80.241,
                "transport_mode": self.mode,
            }
        )
        self.vehicle, _ = Vehicle.objects.get_or_create(
            vehicle_id="BUS-TEST-1",
            defaults={
                "transport_mode": self.mode,
                "current_route": self.route,
                "current_latitude": 12.9905,
                "current_longitude": 80.2405,
                "current_speed": 35.0,
                "status": "MOVING",
                "delay_seconds": 0,
            }
        )

    def test_devops_health_endpoint(self):
        resp = self.client.get("/api/v1/devops/health/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("services", data)
        self.assertIn("telemetry_rates", data)
        self.assertEqual(data["status"], "HEALTHY")

    def test_devops_service_graph(self):
        resp = self.client.get("/api/v1/devops/service-graph/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertGreater(len(data["nodes"]), 4)
        self.assertGreater(len(data["edges"]), 4)

    def test_devops_chaos_experiment(self):
        resp = self.client.post("/api/v1/devops/chaos/trigger/", {"action": "kill_api_pod"}, format="json")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["result"], "RECOVERED")
        self.assertGreater(data["recovery_time_seconds"], 0)

    def test_devops_loadtest(self):
        resp = self.client.post("/api/v1/devops/loadtest/run/", {"vehicles": 1500, "duration_sec": 10}, format="json")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("before", data)
        self.assertIn("after", data)
        self.assertGreater(data["after"]["active_pods"], 2)

    def test_devops_deployments_and_canary(self):
        resp = self.client.get("/api/v1/devops/deployments/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["current_version"], "v1.8.2")

        # Adjust canary split
        resp_canary = self.client.post("/api/v1/devops/deployments/canary/", {"action": "set_split", "split_pct": 25}, format="json")
        self.assertEqual(resp_canary.status_code, 200)
        self.assertEqual(resp_canary.json()["canary_split_pct"], 25)

    def test_devops_incidents(self):
        resp = self.client.get("/api/v1/devops/incidents/")
        self.assertEqual(resp.status_code, 200)
        self.assertGreater(len(resp.json()["incidents"]), 0)

    def test_devops_logs(self):
        resp = self.client.get("/api/v1/devops/logs/?level=INFO")
        self.assertEqual(resp.status_code, 200)
        self.assertGreater(len(resp.json()["logs"]), 0)

    def test_devops_slo(self):
        resp = self.client.get("/api/v1/devops/slo/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("slo_targets", resp.json())

    def test_devops_feature_flags(self):
        resp = self.client.get("/api/v1/devops/feature-flags/")
        self.assertEqual(resp.status_code, 200)
        self.assertGreater(len(resp.json()["flags"]), 0)

    def test_journey_planner(self):
        resp = self.client.get("/api/v1/routes/plan_journey/?from=Current%20Location&to=SASTRA%20University")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["origin"], "Current Location")
        self.assertGreater(len(data["recommended_journey"]), 2)

    def test_vehicle_eta_and_deviation(self):
        resp = self.client.get(f"/api/v1/vehicles/{self.vehicle.vehicle_id}/eta/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("next_stop", data)
        self.assertIn("destination", data)
        self.assertIn("route_deviation", data)
