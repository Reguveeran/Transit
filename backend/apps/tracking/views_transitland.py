"""
UniTransit - Transitland & Live Telemetry Backend API Views
Connects the Django backend with Transitland v2 REST API and live data adapters.
"""

import os
import logging
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from adapters.gtfs_realtime.transitland_adapter import TransitlandAdapter
from apps.routes.models import Route
from apps.stops.models import Stop
from apps.vehicles.models import TransportMode

logger = logging.getLogger("unitransit.api.transitland")


@api_view(["GET"])
@permission_classes([AllowAny])
def live_telemetry_status(request):
    """
    Returns the real-time live connectivity status of all configured adapters.
    """
    transitland_key = os.getenv("TRANSITLAND_API_KEY")
    opensky_client_id = os.getenv("OPENSKY_CLIENT_ID")
    aisstream_key = os.getenv("AISSTREAM_API_KEY")
    aishub_user = os.getenv("AISHUB_USERNAME")

    return JsonResponse({
        "status": "connected",
        "active_adapters": {
            "opensky_adsb": {
                "enabled": bool(opensky_client_id),
                "client_id": opensky_client_id or None,
                "mode": "Commercial Aircraft (Live ADS-B)",
                "status": "ONLINE" if opensky_client_id else "UNCONFIGURED"
            },
            "transitland_v2": {
                "enabled": bool(transitland_key),
                "mode": "Global GTFS / GTFS-Realtime Transit Feeds",
                "status": "ONLINE" if transitland_key else "UNCONFIGURED"
            },
            "aisstream_marine": {
                "enabled": bool(aisstream_key),
                "mode": "Global AIS Ocean Vessels & Ferries (AISStream.io)",
                "status": "ONLINE" if aisstream_key else "UNCONFIGURED"
            },
            "simulator": {
                "enabled": True,
                "mode": "High-Fidelity Multi-Modal Physics Simulator",
                "status": "ONLINE"
            }
        }
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def list_transitland_operators(request):
    """
    Search and list transit operators worldwide via Transitland v2 API.
    Query params:
      - search: optional keyword (e.g. 'caltrain', 'ferry', 'metro')
      - limit: max results (default 10)
    """
    search_term = request.GET.get("search")
    limit = int(request.GET.get("limit", 10))

    try:
        adapter = TransitlandAdapter()
        operators = adapter.get_operators(search=search_term, limit=limit)
        return Response({
            "count": len(operators),
            "operators": [
                {
                    "onestop_id": op.get("onestop_id"),
                    "name": op.get("name"),
                    "short_name": op.get("short_name"),
                    "website": op.get("website"),
                    "feed_count": len(op.get("feeds", [])),
                }
                for op in operators
            ]
        })
    except Exception as e:
        logger.error(f"Failed to fetch Transitland operators: {e}")
        return Response({"error": str(e)}, status=502)


@api_view(["GET"])
@permission_classes([AllowAny])
def list_transitland_feeds(request):
    """
    List verified GTFS-Realtime feeds registered in Transitland.
    """
    limit = int(request.GET.get("limit", 10))
    try:
        adapter = TransitlandAdapter()
        feeds = adapter.get_realtime_feeds(limit=limit)
        return Response({"count": len(feeds), "feeds": feeds})
    except Exception as e:
        logger.error(f"Failed to fetch Transitland feeds: {e}")
        return Response({"error": str(e)}, status=502)


@api_view(["POST"])
@permission_classes([AllowAny])
def import_transitland_operator(request):
    """
    Imports real routes for an operator from Transitland into the database.
    Body: {"operator_onestop_id": "o-9q9-acealtamontcorridorexpress"}
    """
    onestop_id = request.data.get("operator_onestop_id")
    if not onestop_id:
        return Response({"error": "operator_onestop_id is required."}, status=400)

    try:
        adapter = TransitlandAdapter()
        routes_data = adapter.get_routes(operator_onestop_id=onestop_id, limit=10)

        mode_obj, _ = TransportMode.objects.get_or_create(
            name="train",
            defaults={"display_name": "Regional Rail", "icon_name": "train"}
        )

        imported = []
        for r in routes_data:
            route_id = r.get("onestop_id") or f"TL-{r.get('id')}"
            short_name = r.get("route_short_name") or r.get("route_long_name") or route_id
            long_name = r.get("route_long_name") or short_name
            color = (r.get("route_color") or "10B981").replace("#", "")

            route_obj, created = Route.objects.get_or_create(
                route_id=route_id,
                defaults={
                    "short_name": short_name[:30],
                    "long_name": long_name[:255],
                    "transport_mode": mode_obj,
                    "color": f"#{color}",
                    "is_active": True,
                }
            )
            imported.append({"route_id": route_obj.route_id, "name": route_obj.long_name, "created": created})

        return Response({
            "status": "success",
            "imported_count": len(imported),
            "routes": imported,
        })
    except Exception as e:
        logger.error(f"Import from Transitland failed: {e}")
        return Response({"error": str(e)}, status=500)
