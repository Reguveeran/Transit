"""
UniTransit - OpenSky Network (ADS-B Live Aircraft) Telemetry Adapter
Retrieves real-time live flight positions and normalizes them into transport.event.v1.
Supports OpenSky Network OAuth2 Client Credentials authentication.
"""

import os
import sys
import time
import urllib.request
import urllib.parse
import json
import logging
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from adapters.common.event_schema import NormalizedTransportEvent, VehicleStatus

logger = logging.getLogger("unitransit.opensky")

import ssl

def get_ssl_context():
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx

# In-memory OAuth2 token cache
_TOKEN_CACHE = {
    "access_token": None,
    "expires_at": 0,
}


def get_oauth2_token(client_id: str = None, client_secret: str = None) -> str | None:
    """Fetches or reuses cached OAuth2 bearer token from OpenSky Network."""
    client_id = client_id or os.getenv("OPENSKY_CLIENT_ID")
    client_secret = client_secret or os.getenv("OPENSKY_CLIENT_SECRET")

    if not client_id or not client_secret:
        return None

    # Check cache
    now = time.time()
    if _TOKEN_CACHE["access_token"] and now < (_TOKEN_CACHE["expires_at"] - 60):
        return _TOKEN_CACHE["access_token"]

    token_url = "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token"
    data = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }).encode("utf-8")

    req = urllib.request.Request(token_url, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        with urllib.request.urlopen(req, timeout=10, context=get_ssl_context()) as resp:
            token_resp = json.loads(resp.read().decode("utf-8"))
            access_token = token_resp.get("access_token")
            expires_in = token_resp.get("expires_in", 1800)
            _TOKEN_CACHE["access_token"] = access_token
            _TOKEN_CACHE["expires_at"] = now + expires_in
            logger.info("Successfully acquired fresh OpenSky OAuth2 token.")
            return access_token
    except Exception as e:
        logger.error(f"Failed to authenticate with OpenSky OAuth2: {e}")
        return None


def fetch_live_flights(bbox=None, client_id=None, client_secret=None):
    """
    Fetches real live aircraft state vectors from OpenSky Network.
    bbox: (min_lat, max_lat, min_lon, max_lon) - optional regional bounding box
    """
    url = "https://opensky-network.org/api/states/all"
    if bbox:
        url += f"?lamin={bbox[0]}&lamax={bbox[1]}&lomin={bbox[2]}&lomax={bbox[3]}"

    req = urllib.request.Request(url, headers={"User-Agent": "UniTransit-Telemetry-Engine/1.0"})

    token = get_oauth2_token(client_id, client_secret)
    if token:
        req.add_header("Authorization", f"Bearer {token}")

    try:
        with urllib.request.urlopen(req, timeout=12, context=get_ssl_context()) as resp:
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
    9: velocity (m/s), 10: true_track (deg)
    """
    if not vector or len(vector) < 11:
        return None

    icao = str(vector[0]).strip()
    raw_callsign = str(vector[1] or "").strip()
    callsign = raw_callsign or icao.upper()
    lon = vector[5]
    lat = vector[6]
    velocity_mps = vector[9]
    heading = vector[10]
    on_ground = vector[8]
    altitude = vector[7]

    if lat is None or lon is None or velocity_mps is None:
        return None

    try:
        lat = float(lat)
        lon = float(lon)
        spd_mps = float(velocity_mps)
        hdg = float(heading or 0.0)
    except (ValueError, TypeError):
        return None

    # Bounds check
    if not (-90.0 <= lat <= 90.0) or not (-180.0 <= lon <= 180.0):
        return None

    # Convert m/s to km/h (1 m/s = 3.6 km/h)
    speed_kmh = round(spd_mps * 3.6, 1)

    return NormalizedTransportEvent(
        vehicle_id=f"PLANE-{callsign}",
        mode="aircraft",
        route_id=callsign,
        latitude=round(lat, 6),
        longitude=round(lon, 6),
        speed=speed_kmh,
        heading=round(hdg % 360.0, 1),
        status=VehicleStatus.STOPPED.value if on_ground else VehicleStatus.MOVING.value,
        timestamp=datetime.now(timezone.utc).isoformat(),
        metadata={
            "icao24": icao,
            "callsign": callsign,
            "origin_country": vector[2],
            "altitude_m": altitude,
        },
    )
