"""
UniTransit - Main URL Routing Configuration
"""

from django.contrib import admin
from django.urls import include, path
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from common.metrics import metrics_view


def health_check(request):
    return JsonResponse(
        {
            "status": "healthy",
            "service": "unitransit-backend",
            "version": "1.0.0",
        }
    )


def ready_check(request):
    """
    Readiness Probe:
    Verifies that required dependencies (Database and Redis)
    are actively reachable. Returns HTTP 503 if any required component is down.
    """
    from django.db import connection
    from django.conf import settings
    import redis

    db_healthy = False
    redis_healthy = False
    details = {}

    # 1. Test Database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        db_healthy = True
        details["database"] = "connected"
    except Exception as e:
        details["database"] = f"error: {str(e)}"

    # 2. Test Redis connection
    try:
        r = redis.Redis(
            host=getattr(settings, "REDIS_HOST", "localhost"),
            port=int(getattr(settings, "REDIS_PORT", 6379)),
            socket_timeout=1.0,
        )
        if r.ping():
            redis_healthy = True
            details["redis"] = "connected"
        else:
            details["redis"] = "ping failed"
    except Exception as e:
        details["redis"] = f"error: {str(e)}"

    is_ready = db_healthy and redis_healthy
    response_data = {
        "status": "ready" if is_ready else "unready",
        "service": "unitransit-backend",
        **details,
    }

    return JsonResponse(response_data, status=200 if is_ready else 503)


urlpatterns = [
    path("admin/", admin.site.urls),
    # Probes & Metrics
    path("health", health_check, name="health-check"),
    path("ready", ready_check, name="ready-check"),
    path("metrics", metrics_view, name="prometheus-metrics"),
    # OpenAPI Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    # Subsystem APIs (will be attached in Phase 3)
    path("api/v1/vehicles/", include("apps.vehicles.urls")),
    path("api/v1/routes/", include("apps.routes.urls")),
    path("api/v1/stops/", include("apps.stops.urls")),
    path("api/v1/trips/", include("apps.trips.urls")),
    path("api/v1/tracking/", include("apps.tracking.urls")),
    path("api/v1/alerts/", include("apps.alerts.urls")),
    path("api/v1/analytics/", include("apps.analytics.urls")),
    path("api/v1/devops/", include("apps.devops.urls")),
]
