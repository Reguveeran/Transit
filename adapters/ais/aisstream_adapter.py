"""
UniTransit - AISStream.io Marine Adapter
Connects to wss://stream.aisstream.io/v0/stream over WebSocket
and normalizes live global AIS vessel telemetry into canonical transport.event.v1 events.
"""

import asyncio
import json
import logging
import os
import ssl
import time
from datetime import datetime, timezone
from typing import AsyncGenerator, Optional

from dotenv import load_dotenv
load_dotenv()

try:
    import certifi
    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except Exception:
    SSL_CONTEXT = ssl._create_unverified_context()

try:
    import websockets
except ImportError:
    websockets = None

from adapters.common.event_schema import NormalizedTransportEvent

logger = logging.getLogger("unitransit.adapters.aisstream")


def normalize_aisstream_message(data: dict) -> Optional[NormalizedTransportEvent]:
    """Normalizes an AISStream.io JSON message to NormalizedTransportEvent."""
    meta = data.get("MetaData", {})
    pos = data.get("Message", {}).get("PositionReport", {})

    lat = meta.get("latitude")
    lon = meta.get("longitude")
    mmsi = meta.get("MMSI")

    if lat is None or lon is None or mmsi is None:
        return None

    # Filter out invalid GPS coordinates
    if abs(lat) > 90 or abs(lon) > 180 or (lat == 0 and lon == 0):
        return None

    ship_name = (meta.get("ShipName") or f"Vessel-{mmsi}").strip()
    sog_knots = pos.get("Sog", 0.0) or 0.0
    speed_kmh = round(sog_knots * 1.852, 1)  # 1 knot = 1.852 km/h
    cog = pos.get("Cog", 0.0) or 0.0
    heading = pos.get("TrueHeading", cog)
    if heading == 511:  # 511 means heading not available in AIS
        heading = cog

    status = "MOVING" if speed_kmh > 1.0 else "STOPPED"
    now_iso = datetime.now(timezone.utc).isoformat()

    return NormalizedTransportEvent(
        event_id=f"AIS-{mmsi}-{int(time.time())}",
        vehicle_id=f"SHIP-{mmsi}",
        mode="ferry",
        route_id=ship_name[:64],
        latitude=round(float(lat), 6),
        longitude=round(float(lon), 6),
        speed=speed_kmh,
        heading=round(float(heading), 1),
        timestamp=now_iso,
        status=status,
        delay_seconds=0,
        metadata={
            "mmsi": mmsi,
            "ship_name": ship_name,
            "sog_knots": sog_knots,
            "source": "AISStream.io",
        },
    )


async def stream_live_ships(
    api_key: Optional[str] = None,
    bounding_boxes=None,
    limit: Optional[int] = None,
) -> AsyncGenerator[NormalizedTransportEvent, None]:
    """
    Connects to AISStream.io WebSocket and yields normalized ship events.
    """
    if not websockets:
        logger.error("websockets library is required for AISStream.")
        return

    key = api_key or os.getenv("AISSTREAM_API_KEY")
    if not key:
        logger.warning("AISSTREAM_API_KEY is not configured.")
        return

    url = "wss://stream.aisstream.io/v0/stream"
    subscribe_msg = {
        "APIKey": key,
        "BoundingBoxes": bounding_boxes or [[[-90, -180], [90, 180]]],
        "FilterMessageTypes": ["PositionReport"],
    }

    count = 0
    while True:
        try:
            async with websockets.connect(url, ssl=SSL_CONTEXT, ping_interval=20) as ws:
                await ws.send(json.dumps(subscribe_msg))
                logger.info("Connected to AISStream.io WebSocket.")

                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    ev = normalize_aisstream_message(data)
                    if ev:
                        yield ev
                        count += 1
                        if limit and count >= limit:
                            return
        except Exception as e:
            logger.warning(f"AISStream connection interrupted: {e}. Reconnecting in 5s...")
            await asyncio.sleep(5)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Testing AISStream adapter (listening for 3 live ships)...")

    async def main():
        async for ship in stream_live_ships(limit=3):
            print(f"⚓ Normalized Vessel: {ship.vehicle_id} ({ship.route_id}) at {ship.latitude}, {ship.longitude} - {ship.speed} km/h")

    asyncio.run(main())
