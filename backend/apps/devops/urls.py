from django.urls import path
from apps.devops.views import (
    system_health_overview,
    service_dependency_graph,
    trigger_chaos_experiment,
    run_load_test,
    deployments_center,
    canary_action,
    incidents_center,
    centralized_logs,
    slo_and_reliability,
    feature_flags_management,
)

urlpatterns = [
    path("health/", system_health_overview, name="devops-system-health"),
    path("service-graph/", service_dependency_graph, name="devops-service-graph"),
    path("chaos/trigger/", trigger_chaos_experiment, name="devops-chaos-trigger"),
    path("loadtest/run/", run_load_test, name="devops-loadtest-run"),
    path("deployments/", deployments_center, name="devops-deployments"),
    path("deployments/canary/", canary_action, name="devops-canary-action"),
    path("incidents/", incidents_center, name="devops-incidents"),
    path("logs/", centralized_logs, name="devops-logs"),
    path("slo/", slo_and_reliability, name="devops-slo"),
    path("feature-flags/", feature_flags_management, name="devops-feature-flags"),
]
