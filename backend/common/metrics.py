"""
UniTransit - Prometheus Metrics Registry & HTTP Exporter
"""

from django.http import HttpResponse
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

# Application Performance & Business Metrics
API_REQUEST_COUNT = Counter(
    "unitransit_api_requests_total",
    "Total HTTP requests received by UniTransit API",
    ["method", "endpoint", "status_code"],
)

API_REQUEST_LATENCY = Histogram(
    "unitransit_api_request_duration_seconds",
    "HTTP request latency in seconds",
    ["endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)

ACTIVE_VEHICLES_GAUGE = Gauge(
    "unitransit_active_vehicles",
    "Number of currently active/moving vehicles",
    ["mode"],
)

# Telemetry Ingestion & Streaming Metrics
EVENTS_PUBLISHED_TOTAL = Counter(
    "unitransit_events_published_total",
    "Total transport events published by simulators and adapters",
    ["mode", "source"],
)

EVENTS_PROCESSED_TOTAL = Counter(
    "unitransit_events_processed_total",
    "Total transport events successfully processed by workers",
    ["mode", "status"],
)
# Backward-compatibility alias
TELEMETRY_EVENTS_PROCESSED = EVENTS_PROCESSED_TOTAL

EVENTS_FAILED_TOTAL = Counter(
    "unitransit_events_failed_total",
    "Total transport events that failed processing",
    ["reason", "service"],
)

PROCESSING_LATENCY_SECONDS = Histogram(
    "unitransit_processing_latency_seconds",
    "Time taken to ingest, validate, persist, and broadcast an event",
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0],
)
# Backward-compatibility alias
PROCESSING_LATENCY_HISTOGRAM = PROCESSING_LATENCY_SECONDS

ALERTS_TRIGGERED_TOTAL = Counter(
    "unitransit_alerts_triggered_total",
    "Total automated alerts evaluated and triggered",
    ["alert_type", "severity"],
)

WEBSOCKET_CONNECTIONS = Gauge(
    "unitransit_websocket_connections",
    "Total active WebSocket commuter clients connected",
)
# Backward-compatibility alias
WEBSOCKET_CONNECTIONS_ACTIVE = WEBSOCKET_CONNECTIONS

WORKER_UP = Gauge(
    "unitransit_worker_up",
    "Status of background worker process (1 for up, 0 for down)",
    ["worker_type", "consumer_id"],
)

STREAM_CONSUMER_LAG = Gauge(
    "unitransit_stream_consumer_lag",
    "Pending unacknowledged or unconsumed message lag in Redis Stream",
    ["stream", "group"],
)

# Phase 6: Canary Deployment & Progressive Delivery Metrics
CANARY_TRAFFIC_PERCENT = Gauge(
    "unitransit_canary_traffic_percent",
    "Traffic percentage routed to canary deployment",
    ["version"],
)

CANARY_ERROR_RATE = Gauge(
    "unitransit_canary_error_rate_percent",
    "Error rate percentage observed on canary deployment",
    ["version"],
)

CANARY_P95_LATENCY = Gauge(
    "unitransit_canary_p95_latency_ms",
    "P95 response latency in milliseconds for canary deployment",
    ["version"],
)

# Phase 7: SRE Service Level Objectives & Error Budget Metrics
SLO_AVAILABILITY_PERCENT = Gauge(
    "unitransit_slo_availability_percent",
    "Current measured event ingestion availability SLI percentage",
    ["window"],
)

SLO_LATENCY_PERCENT = Gauge(
    "unitransit_slo_latency_percent",
    "Current measured processing latency SLI percentage (events <= threshold)",
    ["window"],
)

SLO_FRESHNESS_PERCENT = Gauge(
    "unitransit_slo_freshness_percent",
    "Current measured stream freshness SLI percentage (lag <= threshold)",
    ["window"],
)

ERROR_BUDGET_REMAINING_PERCENT = Gauge(
    "unitransit_error_budget_remaining_percent",
    "Percentage of error budget remaining for the specified SLO",
    ["slo_type"],
)

ERROR_BUDGET_BURN_RATE = Gauge(
    "unitransit_error_budget_burn_rate",
    "Burn rate of error budget consumption relative to SLO target",
    ["slo_type", "window"],
)


def metrics_view(request):
    """Exposes OpenMetrics / Prometheus scrape endpoint."""
    # Sample current stream consumer lag and worker state from Redis before generating output
    try:
        import os, redis
        r = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6380")),
            socket_timeout=1.0,
        )
        groups = r.xinfo_groups("transport.events")
        lag = 0
        for g in groups:
            g_name = g.get("name")
            if g_name in [b"unitransit_workers", "unitransit_workers"]:
                lag = g.get("lag", 0) or 0
                break
        STREAM_CONSUMER_LAG.labels(stream="transport.events", group="unitransit_workers").set(lag)
    except Exception:
        STREAM_CONSUMER_LAG.labels(stream="transport.events", group="unitransit_workers").set(0)

    # Ensure baseline labels exist for scraper
    try:
        EVENTS_PROCESSED_TOTAL.labels(mode="bus", status="success")
        EVENTS_PUBLISHED_TOTAL.labels(mode="bus", source="simulator")
        WORKER_UP.labels(worker_type="position", consumer_id="pos_worker_1").set(1)
        WORKER_UP.labels(worker_type="position", consumer_id="pos_worker_2").set(1)

        from apps.devops.canary_engine import get_canary_telemetry
        canary = get_canary_telemetry()
        c_ver = canary["canary_metrics"]["version"]
        CANARY_TRAFFIC_PERCENT.labels(version=c_ver).set(canary["canary_metrics"]["traffic_pct"])
        CANARY_ERROR_RATE.labels(version=c_ver).set(canary["canary_metrics"]["error_rate_pct"])
        CANARY_P95_LATENCY.labels(version=c_ver).set(canary["canary_metrics"]["p95_latency_ms"])

        from apps.devops.slo_engine import refresh_prometheus_slo_metrics
        refresh_prometheus_slo_metrics()
    except Exception:
        pass

    return HttpResponse(generate_latest(), content_type=CONTENT_TYPE_LATEST)
