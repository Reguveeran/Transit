"""
UniTransit - OpenSky Network (ADS-B Live Aircraft) Telemetry Adapter
Retrieves real-time live flight positions and normalizes them into transport.event.v1.

Provider: https://opensky-network.org/
Free API: No API key strictly required for basic public feeds (10s rate limit),
          or provide username/password in .env for higher rate limits.
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

logger = logging.getLogger("unitransit.opensky")


def fetch_live_flights(bbox=None, username=None, password=None):
    """
    Fetches live aircraft state vectors from OpenSky Network REST API.
    bbox: (min_lat, max_lat, min_lon, max_lon) - optional bounding box
    """
    url = "https://opensky-network.org/api/states/all"
    if bbox:
        url += f"?lamin={bbox[0]}&lamax={bbox[1]}&lomin={bbox[2]}&lomax={bbox[3]}"

    req = urllib.request.Request(url, headers={"User-Agent": "UniTransit-Adapter/1.0"})

    if username and password:
        import base64
        credentials = f"{username}:{password}".encode("ascii")
        req.add_header("Authorization", f"Basic {base64.b64encode(credentials).decode('ascii')}")

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("states", [])
    except Exception as e:
        logger.error(f"Error querying OpenSky Network API: {e}")
        return []


def normalize_opensky_vector(vector):
    """
    OpenSky State Vector Indices:
    0: icao24, 1: callsign, 2: origin_country, 3: time_position,
    5: longitude, 6: latitude, 7: baro_altitude, 8: on_ground,
    9: velocity (m/s), 10: true_track (deg), 11: vertical_rate
    """
    if not vector or len(vector) < 11:
        return None

    icao = vector[0]
    callsign = (vector[1] or icao).strip()
    lon = vector[5]
    lat = vector[6]
    velocity_mps = vector[9]
    heading = vector[10]
    on_ground = vector[8]

    if lat is None or lon is None or velocity_mps is None:
        return None

    # Convert m/s to km/h
    speed_kmh = round(velocity_mps * 3.6, 1)

    return NormalizedTransportEvent(
        vehicle_id=f"FLIGHT-{callsign or icao}",
        mode="aircraft",
        route_id=callsign or "COMMERCIAL-AIR",
        latitude=round(lat, 6),
        longitude=round(lon, 6),
        speed=speed_kmh,
        heading=round(heading or 0.0, 1),
        status=VehicleStatus.STOPPED.value if on_ground else VehicleStatus.MOVING.value,
        timestamp=datetime.now(timezone.utc).isoformat(),
        metadata={"icao24": icao, "callsign": callsign, "altitude_m": vector[7]},
    )
