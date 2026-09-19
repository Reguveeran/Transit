"""
UniTransit - GTFS-Realtime (Buses, Metro & Trains) Telemetry Adapter
Polls agency GTFS-RT protocol buffer feeds and normalizes vehicle positions.

Example public feeds:
- Transitland / TransitFeeds / National Transit Database
- NYC MTA: https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs
- London TfL: https://api.tfl.gov.uk/
- MBTA: https://api-v3.mbta.com/vehicle_positions
"""

import os
import sys
import time
import urllib.request
import json
import logging
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from adapters.common.event_schema import NormalizedTransportEvent, VehicleStatus

logger = logging.getLogger("unitransit.gtfs_rt")


def fetch_gtfs_rt_feed(feed_url: str, api_key: str = None, headers: dict = None):
    """Fetches GTFS-RT feed (JSON or Protobuf) from transit authority."""
    req_headers = {"User-Agent": "UniTransit-Adapter/1.0"}
    if api_key:
        req_headers["x-api-key"] = api_key
        req_headers["Authorization"] = f"Bearer {api_key}"
    if headers:
        req_headers.update(headers)

    req = urllib.request.Request(feed_url, headers=req_headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read()
    except Exception as e:
        logger.error(f"Failed to fetch GTFS-RT from {feed_url}: {e}")
        return None


def normalize_gtfs_entity(entity, default_mode="bus"):
    """Normalizes a GTFS-RT VehiclePosition entity into transport.event.v1."""
    veh = entity.get("vehicle", {})
    pos = veh.get("position", {})
    trip = veh.get("trip", {})
    desc = veh.get("vehicle", {})

    lat = pos.get("latitude")
    lon = pos.get("longitude")
    if lat is None or lon is None:
        return None

    speed_mps = pos.get("speed", 0.0) or 0.0
    speed_kmh = round(speed_mps * 3.6, 1) if speed_mps else 30.0

    return NormalizedTransportEvent(
        vehicle_id=desc.get("id") or desc.get("label") or f"GTFS-{trip.get('trip_id', 'UNKNOWN')}",
        mode=default_mode,
        route_id=trip.get("route_id") or "GTFS-ROUTE",
        trip_id=trip.get("trip_id"),
        latitude=round(float(lat), 6),
        longitude=round(float(lon), 6),
        speed=speed_kmh,
        heading=round(float(pos.get("bearing", 0.0)), 1),
        status=VehicleStatus.MOVING.value if speed_kmh > 1.0 else VehicleStatus.STOPPED.value,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
