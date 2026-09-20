"""
UniTransit - Phase 7 SLO Engine & Error Budget Test Suite
=========================================================
Verifies:
1. Healthy system SLIs satisfy SLO targets with 100% budget and sub-1.0x burn rate.
2. Degraded availability reduces Availability SLI, consumes budget, and elevates burn rate.
3. Degraded latency reduces Latency SLI below 95%, consumes latency budget.
4. Excessive consumer lag reduces Stream Freshness SLI below 99%.
5. Mathematical precision of Error Budget (Total, Consumed, Remaining).
6. Multi-window Burn Rate calculations (Short 5m vs Long 30m).
7. API responses for /api/v1/devops/slo/ and /api/v1/devops/error-budget/.
8. Prometheus metrics scrape export for all unitransit_slo_* and unitransit_error_budget_* gauges.
9. Controlled SRE experiment execution (Phase 7G).
"""

import json
from django.test import TestCase
from rest_framework.test import APIClient

from apps.devops.slo_engine import (
    SLOObjectiveConfig,
    TelemetryObservation,
    calculate_sli_from_observations,
    compute_error_budget,
    compute_burn_rate,
    get_slo_report,
    get_error_budget_summary,
    configure_slo_targets,
    execute_controlled_slo_experiment,
    _BUFFER,
)


class SLOEngineAndErrorBudgetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        _BUFFER.reset_to_baseline()
        # Reset default configuration
        configure_slo_targets(
            availability_target=99.90,
            latency_target=95.00,
            latency_threshold_ms=50.0,
            freshness_target=99.00,
            freshness_lag_threshold_sec=0.20,
        )

    def test_healthy_system_slo_and_budget(self):
        """Validates that a healthy baseline system satisfies all SLOs with zero burn."""
        report = get_slo_report(force_local_buffer=True)

        self.assertEqual(report["overall_status"], "HEALTHY")
        self.assertLessEqual(report["max_burn_rate"], 1.0)
        self.assertEqual(report["policy"]["deployment_action"], "PROCEED")
        self.assertEqual(report["policy"]["canary_recommendation"], "PROCEED")

        # Availability
        self.assertGreaterEqual(report["availability"]["sli"], 99.9)
        self.assertGreaterEqual(report["availability"]["error_budget_remaining"], 90.0)

        # Latency
        self.assertGreaterEqual(report["latency"]["sli"], 95.0)
        self.assertGreaterEqual(report["latency"]["error_budget_remaining"], 90.0)

        # Freshness
        self.assertGreaterEqual(report["freshness"]["sli"], 99.0)
        self.assertGreaterEqual(report["freshness"]["error_budget_remaining"], 90.0)

        # Backward compatibility with existing tests
        self.assertIn("slo_targets", report)
        self.assertIn("api_availability", report["slo_targets"])
        self.assertIn("websocket_delivery", report["slo_targets"])
        self.assertIn("p95_latency", report["slo_targets"])

    def test_degraded_availability_slo(self):
        """Injects high failed events and verifies availability SLI drops, consuming budget."""
        config = SLOObjectiveConfig(availability_target_pct=99.90)

        # 80 successful, 20 failed -> 80.0% availability
        samples = [
            TelemetryObservation(
                timestamp=100.0,
                events_successful=80,
                events_failed=20,
                latencies_ms=[15.0, 20.0],
                consumer_lag_sec=0.02,
            )
        ]
        sli = calculate_sli_from_observations(samples, config)
        self.assertEqual(sli["availability_sli"], 80.0)

        budget = compute_error_budget(config.availability_target_pct, sli["availability_sli"])
        # Allowed error is 0.1%, observed is 20.0% -> budget consumed is 100%
        self.assertEqual(budget["error_budget_consumed"], 100.0)
        self.assertEqual(budget["error_budget_remaining"], 0.0)
        self.assertEqual(budget["status"], "EXHAUSTED")

        burn_rate = compute_burn_rate(config.availability_target_pct, sli["availability_sli"])
        # Burn rate = 20.0 / 0.1 = 200.0x
        self.assertGreater(burn_rate, 100.0)

    def test_degraded_latency_slo(self):
        """Injects slow events (> 50ms) and verifies latency SLI drops, consuming budget."""
        config = SLOObjectiveConfig(latency_target_pct=95.00, latency_threshold_ms=50.0)

        # 4 events > 50ms, 1 event <= 50ms -> 20.0% compliance (SLO 95.0%)
        samples = [
            TelemetryObservation(
                timestamp=100.0,
                events_successful=100,
                events_failed=0,
                latencies_ms=[65.0, 75.0, 90.0, 110.0, 25.0],
                consumer_lag_sec=0.02,
            )
        ]
        sli = calculate_sli_from_observations(samples, config)
        self.assertEqual(sli["latency_sli"], 20.0)

        budget = compute_error_budget(config.latency_target_pct, sli["latency_sli"])
        # Allowed error = 5.0%, observed error = 80.0% -> 100% consumed
        self.assertEqual(budget["error_budget_consumed"], 100.0)
        self.assertEqual(budget["error_budget_remaining"], 0.0)
        self.assertEqual(budget["status"], "EXHAUSTED")

        burn_rate = compute_burn_rate(config.latency_target_pct, sli["latency_sli"])
        # Burn rate = 80.0 / 5.0 = 16.0x
        self.assertEqual(burn_rate, 16.0)

    def test_excessive_consumer_lag_freshness_slo(self):
        """Injects excessive Redis consumer lag (> 200ms) and verifies freshness SLI drops."""
        config = SLOObjectiveConfig(freshness_target_pct=99.00, freshness_lag_threshold_sec=0.20)

        # 3 samples with high lag, 1 with low lag -> 25.0% compliance (SLO 99.0%)
        samples = [
            TelemetryObservation(timestamp=1.0, events_successful=10, events_failed=0, consumer_lag_sec=0.85),
            TelemetryObservation(timestamp=2.0, events_successful=10, events_failed=0, consumer_lag_sec=1.20),
            TelemetryObservation(timestamp=3.0, events_successful=10, events_failed=0, consumer_lag_sec=0.45),
            TelemetryObservation(timestamp=4.0, events_successful=10, events_failed=0, consumer_lag_sec=0.05),
        ]
        sli = calculate_sli_from_observations(samples, config)
        self.assertEqual(sli["freshness_sli"], 25.0)
        self.assertEqual(sli["peak_consumer_lag_sec"], 1.20)

        budget = compute_error_budget(config.freshness_target_pct, sli["freshness_sli"])
        self.assertEqual(budget["error_budget_remaining"], 0.0)
        self.assertEqual(budget["status"], "EXHAUSTED")

        burn_rate = compute_burn_rate(config.freshness_target_pct, sli["freshness_sli"])
        # Allowed = 1.0%, observed = 75.0% -> 75.0x
        self.assertEqual(burn_rate, 75.0)

    def test_error_budget_calculation_accuracy(self):
        """Tests exact mathematical accuracy of error budget total, consumed, and remaining."""
        # 1. 100% SLI -> 0% consumed, 100% remaining
        b1 = compute_error_budget(99.90, 100.0)
        self.assertEqual(b1["error_budget_total_allowed_pct"], 0.1)
        self.assertEqual(b1["error_budget_consumed"], 0.0)
        self.assertEqual(b1["error_budget_remaining"], 100.0)
        self.assertEqual(b1["status"], "HEALTHY")

        # 2. 99.95% SLI with 99.90% SLO -> 0.05% error out of 0.10% allowed -> 50% consumed, 50% remaining
        b2 = compute_error_budget(99.90, 99.95)
        self.assertEqual(b2["error_budget_consumed"], 50.0)
        self.assertEqual(b2["error_budget_remaining"], 50.0)
        self.assertEqual(b2["status"], "HEALTHY")

        # 3. 99.91% SLI with 99.90% SLO -> 0.09% error -> 90% consumed, 10% remaining -> AT_RISK
        b3 = compute_error_budget(99.90, 99.91)
        self.assertEqual(b3["error_budget_consumed"], 90.0)
        self.assertEqual(b3["error_budget_remaining"], 10.0)
        self.assertEqual(b3["status"], "AT_RISK")

        # 4. 99.80% SLI with 99.90% SLO -> 0.20% error -> 100% consumed, 0% remaining -> EXHAUSTED
        b4 = compute_error_budget(99.90, 99.80)
        self.assertEqual(b4["error_budget_consumed"], 100.0)
        self.assertEqual(b4["error_budget_remaining"], 0.0)
        self.assertEqual(b4["status"], "EXHAUSTED")

    def test_burn_rate_calculations(self):
        """Verifies burn rate formulas across various SLI/SLO combinations."""
        # Perfect compliance -> burn rate = 0.0
        self.assertEqual(compute_burn_rate(99.90, 100.0), 0.0)

        # Half allowed error -> burn rate = 0.5
        self.assertEqual(compute_burn_rate(99.90, 99.95), 0.5)

        # Exact allowed error -> burn rate = 1.0
        self.assertEqual(compute_burn_rate(99.90, 99.90), 1.0)

        # 2x allowed error -> burn rate = 2.0
        self.assertEqual(compute_burn_rate(99.90, 99.80), 2.0)

        # 10x allowed error -> burn rate = 10.0
        self.assertEqual(compute_burn_rate(99.90, 99.00), 10.0)

    def test_slo_api_endpoints(self):
        """Tests GET /api/v1/devops/slo/ and POST target configuration."""
        # GET /api/v1/devops/slo/
        resp = self.client.get("/api/v1/devops/slo/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        self.assertIn("overall_status", data)
        self.assertIn("availability", data)
        self.assertIn("latency", data)
        self.assertIn("freshness", data)
        self.assertIn("policy", data)
        self.assertIn("burn_rate_formula", data)
        self.assertIn("slo_targets", data)

        # Check availability sub-structure
        avail = data["availability"]
        self.assertIn("sli", avail)
        self.assertIn("slo", avail)
        self.assertIn("error_budget_remaining", avail)
        self.assertIn("burn_rate_short", avail)
        self.assertIn("burn_rate_long", avail)

        # POST /api/v1/devops/slo/ to dynamically update targets
        update_resp = self.client.post("/api/v1/devops/slo/", {
            "availability_target": 99.95,
            "latency_target": 98.0,
            "latency_threshold_ms": 40.0,
        }, format="json")
        self.assertEqual(update_resp.status_code, 200)
        updated_data = update_resp.json()
        self.assertEqual(updated_data["availability"]["slo"], 99.95)
        self.assertEqual(updated_data["latency"]["slo"], 98.0)
        self.assertEqual(updated_data["latency"]["objective_threshold_ms"], 40.0)

    def test_error_budget_api_endpoint(self):
        """Tests GET /api/v1/devops/error-budget/."""
        resp = self.client.get("/api/v1/devops/error-budget/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        self.assertIn("status", data)
        self.assertIn("policy", data)
        self.assertIn("error_budgets", data)
        self.assertIn("availability", data["error_budgets"])
        self.assertIn("latency", data["error_budgets"])
        self.assertIn("freshness", data["error_budgets"])

    def test_prometheus_metrics_scrape_export(self):
        """Verifies Prometheus /metrics endpoint exports all new Phase 7 gauges."""
        resp = self.client.get("/metrics")
        self.assertEqual(resp.status_code, 200)

        # Verify SLO metrics are present in scrape content
        self.assertIn(b"unitransit_slo_availability_percent", resp.content)
        self.assertIn(b"unitransit_slo_latency_percent", resp.content)
        self.assertIn(b"unitransit_slo_freshness_percent", resp.content)
        self.assertIn(b"unitransit_error_budget_remaining_percent", resp.content)
        self.assertIn(b"unitransit_error_budget_burn_rate", resp.content)

    def test_controlled_slo_experiment_execution(self):
        """Executes Phase 7G controlled SRE experiment and verifies all 3 stages."""
        # Run experiment directly via python engine
        exp = execute_controlled_slo_experiment()
        self.assertIn("stages", exp)
        self.assertEqual(len(exp["stages"]), 3)

        stage1 = exp["stages"][0]
        self.assertEqual(stage1["name"], "Healthy Baseline")
        self.assertGreaterEqual(stage1["availability_sli"], 99.0)
        self.assertEqual(stage1["policy"], "PROCEED")

        stage2 = exp["stages"][1]
        self.assertEqual(stage2["name"], "Controlled Fault Injection & Degradation")
        # Injected fault should have degraded availability, latency, and freshness
        self.assertLess(stage2["availability_sli"], 99.0)
        self.assertLess(stage2["latency_sli"], 95.0)
        self.assertLess(stage2["freshness_sli"], 99.0)
        self.assertGreater(stage2["burn_rate"], 1.0)
        self.assertIn(stage2["policy"], ["PAUSE_DEPLOYMENTS", "FREEZE_DEPLOYMENTS"])

        stage3 = exp["stages"][2]
        self.assertEqual(stage3["name"], "Recovery & Stabilization")
        self.assertGreaterEqual(stage3["availability_sli"], 95.0)
        self.assertEqual(stage3["policy"], "PROCEED")

        # Test POST API endpoint
        post_resp = self.client.post("/api/v1/devops/slo/experiment/", {}, format="json")
        self.assertEqual(post_resp.status_code, 200)
        self.assertEqual(post_resp.json()["status"], "success")
        self.assertIn("trial", post_resp.json())

        # Test GET API endpoint
        get_resp = self.client.get("/api/v1/devops/slo/experiment/")
        self.assertEqual(get_resp.status_code, 200)
        self.assertGreater(len(get_resp.json()["trials"]), 0)

    def test_promql_query_execution_and_fallback(self):
        """Verifies PromQL authoritative calculation when Prometheus is reachable, and fallback on failure."""
        from unittest.mock import patch
        from apps.devops.slo_engine import calculate_slis_from_promql, get_slo_config

        # 1. Test PromQL resolution with mock/live vectors
        with patch("apps.devops.slo_engine.query_prometheus_promql", side_effect=[99.98, 97.4, 99.5]):
            prom_sli = calculate_slis_from_promql(get_slo_config(), window="5m")
            self.assertIsNotNone(prom_sli)
            self.assertEqual(prom_sli["availability_sli"], 99.98)
            self.assertEqual(prom_sli["latency_sli"], 97.4)
            self.assertEqual(prom_sli["freshness_sli"], 99.5)
            self.assertIn("promql_queries", prom_sli)

        # 2. Test fallback when Prometheus query returns None (e.g. network down)
        with patch("apps.devops.slo_engine.query_prometheus_promql", return_value=None):
            report = get_slo_report()
            self.assertEqual(report["telemetry_source"], "in_process_fallback")
