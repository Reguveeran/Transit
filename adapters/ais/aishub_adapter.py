"""
UniTransit - AISHub (Marine Vessels, Ships & Ferries) Telemetry Adapter
Retrieves live marine AIS positions via AISHub WebService and normalizes them.

Provider: https://www.aishub.net/api
Format: JSON / CSV / NMEA
"""

import os
import sys
import urllib.request
import json
import logging
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from adapters.common.event_schema import NormalizedTransportEvent, VehicleStatus

logger = logging.getLogger("unitransit.aishub")


def fetch_aishub_ships(username: str, format_type: str = "1", bbox=None):
    """
    Fetches live vessel positions from AISHub API.
    username: AISHub API registered username
    format_type: 1 for JSON
    """
    url = f"https://data.aishub.net/ws.php?username={username}&format={format_type}&output=json"
    if bbox:
        url += f"&latmin={bbox[0]}&latmax={bbox[1]}&lonmin={bbox[2]}&lonmax={bbox[3]}"

    req = urllib.request.Request(url, headers={"User-Agent": "UniTransit-Adapter/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if isinstance(data, list) and len(data) > 1:
                return data[1]  # Vessel records array
            return []
    except Exception as e:
        logger.error(f"Error fetching AISHub data: {e}")
        return []


def normalize_ais_record(record):
    """Normalizes an AISHub vessel record into transport.event.v1."""
    mmsi = record.get("MMSI")
    name = (record.get("NAME") or f"SHIP-{mmsi}").strip()
    lat = record.get("LATITUDE")
    lon = record.get("LONGITUDE")
    sog = record.get("SOG", 0.0)  # Speed over ground in knots
    cog = record.get("COG", 0.0)  # Course over ground in degrees

    if lat is None or lon is None:
        return None

    # Convert knots to km/h (1 knot = 1.852 km/h)
    speed_kmh = round(float(sog) * 1.852, 1)

    return NormalizedTransportEvent(
        vehicle_id=f"VESSEL-{mmsi}",
        mode="ferry",
        route_id=record.get("DEST", "COASTAL-ROUTE"),
        latitude=round(float(lat), 6),
        longitude=round(float(lon), 6),
        speed=speed_kmh,
        heading=round(float(cog), 1),
        status=VehicleStatus.MOVING.value if speed_kmh > 0.5 else VehicleStatus.STOPPED.value,
        timestamp=datetime.now(timezone.utc).isoformat(),
        metadata={"mmsi": mmsi, "vessel_name": name},
    )
