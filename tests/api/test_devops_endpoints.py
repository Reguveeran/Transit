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

    def test_devops_worker_pool_and_scale(self):
        resp = self.client.get("/api/v1/devops/workers/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("worker_pool", data)

        scale_resp = self.client.post("/api/v1/devops/workers/scale/", {"target": 2}, format="json")
        self.assertEqual(scale_resp.status_code, 200)
        self.assertEqual(scale_resp.json()["status"], "success")

    def test_devops_benchmark_history_and_run(self):
        resp = self.client.get("/api/v1/devops/benchmark/history/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("vehicle_load", data)
        self.assertIn("worker_scaling", data)
        self.assertIn("failure_trials", data)
        self.assertGreater(len(data["vehicle_load"]), 0)
        self.assertIn("p95_latency_ms", data["vehicle_load"][0])
        self.assertIn("peak_pel", data["vehicle_load"][0])

        run_resp = self.client.post("/api/v1/devops/benchmark/run/", {
            "experiment_type": "vehicle_load",
            "vehicles": 50,
            "workers": 1,
            "duration_sec": 1,
        }, format="json")
        self.assertEqual(run_resp.status_code, 200)
        self.assertEqual(run_resp.json()["status"], "success")
        self.assertIn("benchmark", run_resp.json())
        self.assertIn("p95_latency_ms", run_resp.json()["benchmark"])

    def test_devops_benchmark_failover(self):
        # GET failure trial history
        resp = self.client.get("/api/v1/devops/benchmark/failover/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("trial", data)
        self.assertEqual(data["trial"]["lost_events"], 0)
        self.assertEqual(data["trial"]["result"], "SUCCESS")

        # POST controlled failure trial
        post_resp = self.client.post("/api/v1/devops/benchmark/failover/", {
            "vehicles": 50,
            "initial_workers": 2,
            "duration_sec": 1,
        }, format="json")
        self.assertEqual(post_resp.status_code, 200)
        post_data = post_resp.json()
        self.assertEqual(post_data["status"], "success")
        self.assertEqual(post_data["trial"]["lost_events"], 0)
        self.assertEqual(post_data["trial"]["result"], "SUCCESS")

    def test_devops_kubernetes_observability(self):
        resp = self.client.get("/api/v1/devops/kubernetes/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("pod_count", data)
        self.assertIn("desired_replicas", data)
        self.assertIn("ready_replicas", data)
        self.assertIn("worker_status", data)
        self.assertIn("redis_stream_length", data)
        self.assertIn("consumer_lag_sec", data)
        self.assertIn("pending_pel_count", data)

    def test_devops_autoscaling_experiment(self):
        # GET history
        resp = self.client.get("/api/v1/devops/autoscaling/experiment/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("latest", data)
        self.assertEqual(len(data["latest"]["stages"]), 4)
        self.assertEqual(data["latest"]["metrics_summary"]["lost_events"], 0)

        # POST run live autoscaling trial
        post_resp = self.client.post("/api/v1/devops/autoscaling/experiment/", {}, format="json")
        self.assertEqual(post_resp.status_code, 200)
        post_data = post_resp.json()
        self.assertEqual(post_data["status"], "success")
        self.assertIn("trial", post_data)
        self.assertEqual(len(post_data["trial"]["stages"]), 4)

    def test_devops_rolling_deploy_api(self):
        resp = self.client.post("/api/v1/devops/deployments/rollout/", {
            "target_tag": "sha-e9b4d1c"
        }, format="json")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("deployment_status", data)
        self.assertEqual(data["deployment_status"]["name"], "worker-position")
        self.assertGreater(data["deployment_status"]["desired"], 0)
        self.assertGreater(data["deployment_status"]["ready"], 0)
        self.assertIn("logs", data)

    def test_devops_rollback_experiment_api(self):
        # Test GET historical/seeded trial
        get_resp = self.client.get("/api/v1/devops/deployments/rollback-experiment/")
        self.assertEqual(get_resp.status_code, 200)
        get_data = get_resp.json()
        self.assertEqual(get_data["status"], "success")
        self.assertIn("latest", get_data)
        self.assertEqual(get_data["latest"]["metrics"]["lost_events"], 0)
        self.assertIn("timeline", get_data["latest"])

        # Test POST trigger controlled rollback experiment
        post_resp = self.client.post("/api/v1/devops/deployments/rollback-experiment/", {}, format="json")
        self.assertEqual(post_resp.status_code, 200)
        post_data = post_resp.json()
        self.assertEqual(post_data["status"], "success")
        self.assertIn("trial", post_data)
        self.assertEqual(post_data["trial"]["metrics"]["lost_events"], 0)
        self.assertGreater(post_data["trial"]["metrics"]["failure_detection_time_sec"], 0)
        self.assertGreater(post_data["trial"]["metrics"]["total_recovery_time_sec"], 0)

    def test_devops_canary_telemetry_api(self):
        resp = self.client.get("/api/v1/devops/deployments/canary/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("telemetry", data)
        self.assertIn("stable_metrics", data["telemetry"])
        self.assertIn("canary_metrics", data["telemetry"])
        self.assertIn("sla_evaluations", data["telemetry"])
        self.assertIn("decision", data["telemetry"])

    def test_devops_canary_step_action_api(self):
        # Step Promote
        promote_resp = self.client.post("/api/v1/devops/deployments/canary/", {"action": "promote"}, format="json")
        self.assertEqual(promote_resp.status_code, 200)
        self.assertEqual(promote_resp.json()["status"], "success")

        # Rollback
        rollback_resp = self.client.post("/api/v1/devops/deployments/canary/", {"action": "rollback"}, format="json")
        self.assertEqual(rollback_resp.status_code, 200)
        self.assertEqual(rollback_resp.json()["status"], "success")
        self.assertEqual(rollback_resp.json()["telemetry"]["canary_split_pct"], 0)

    def test_devops_canary_healthy_trial_api(self):
        resp = self.client.post("/api/v1/devops/deployments/canary/experiment/", {"trial_type": "healthy_rollout"}, format="json")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["trial"]["final_result"], "PROMOTION_SUCCESSFUL")
        self.assertEqual(len(data["trial"]["stages"]), 4)
        self.assertEqual(data["trial"]["metrics_summary"]["lost_events"], 0)

    def test_devops_canary_faulty_rollback_api(self):
        resp = self.client.post("/api/v1/devops/deployments/canary/experiment/", {"trial_type": "faulty_rollback"}, format="json")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["trial"]["final_result"], "AUTO_ROLLED_BACK")
        self.assertEqual(data["trial"]["metrics_summary"]["lost_events"], 0)
        self.assertLessEqual(data["trial"]["metrics_summary"]["detection_time_seconds"], 2.0)
        self.assertGreater(data["trial"]["metrics_summary"]["total_recovery_seconds"], 0)
