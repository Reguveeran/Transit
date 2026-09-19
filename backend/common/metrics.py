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

TELEMETRY_EVENTS_PROCESSED = Counter(
    "unitransit_telemetry_events_processed_total",
    "Total normalized transport events processed by worker pool",
    ["mode", "status"],
)

PROCESSING_LATENCY_HISTOGRAM = Histogram(
    "unitransit_event_processing_latency_seconds",
    "Time taken to ingest, validate, persist, and broadcast an event",
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0],
)

ALERTS_TRIGGERED_TOTAL = Counter(
    "unitransit_alerts_triggered_total",
    "Total automated alerts evaluated and triggered",
    ["alert_type", "severity"],
)

WEBSOCKET_CONNECTIONS_ACTIVE = Gauge(
    "unitransit_websocket_connections_active",
    "Total active WebSocket commuter clients connected",
)


def metrics_view(request):
    """Exposes OpenMetrics / Prometheus scrape endpoint."""
    return HttpResponse(generate_latest(), content_type=CONTENT_TYPE_LATEST)
