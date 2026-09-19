"""
UniTransit - Main URL Routing Configuration
"""

from django.contrib import admin
from django.urls import include, path
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def health_check(request):
    return JsonResponse(
        {
            "status": "healthy",
            "service": "unitransit-backend",
            "version": "1.0.0",
        }
    )


def ready_check(request):
    return JsonResponse(
        {
            "status": "ready",
            "database": "connected",
            "redis": "connected",
        }
    )


urlpatterns = [
    path("admin/", admin.site.urls),
    # Probes
    path("health", health_check, name="health-check"),
    path("ready", ready_check, name="ready-check"),
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
]
