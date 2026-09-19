"""
Transitland v2 API Adapter for UniTransit.
Queries the global Transitland v2 REST API (https://transit.land/api/v2/rest)
using the Interline Web Access / Live Transitland API Key.

Provides access to:
- Transit operators worldwide
- Feed registry (GTFS static & GTFS-Realtime live vehicle position feeds)
- Route geometries and vehicle positioning
"""

import os
import json
import logging
import ssl
import urllib.request
import urllib.parse
from typing import List, Dict, Any, Optional
from adapters.common.event_schema import NormalizedTransportEvent
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("unitransit.adapters.transitland")

try:
    import certifi
    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except Exception:
    SSL_CONTEXT = ssl._create_unverified_context()


class TransitlandAdapter:
    BASE_URL = "https://transit.land/api/v2/rest"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("TRANSITLAND_API_KEY", "")

    def _request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Perform an authenticated GET request to Transitland v2 REST API."""
        if not self.api_key:
            raise ValueError("Transitland API key is missing. Set TRANSITLAND_API_KEY in .env.")

        query_params = params.copy() if params else {}
        query_params["apikey"] = self.api_key
        query_str = "&".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in query_params.items())

        url = f"{self.BASE_URL}/{endpoint}?{query_str}"
        headers = {
            "User-Agent": "UniTransit-Telemetry-Engine/1.0",
            "Accept": "application/json"
        }
        req = urllib.request.Request(url, headers=headers)

        try:
            with urllib.request.urlopen(req, timeout=12, context=SSL_CONTEXT) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as e:
            logger.error("Transitland request to %s failed: %s", endpoint, e)
            raise

    def get_operators(self, search: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve transit agencies/operators."""
        params = {"limit": limit}
        if search:
            params["search"] = search
        data = self._request("operators", params)
        return data.get("operators", [])

    def get_realtime_feeds(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Find active GTFS-Realtime feeds with live vehicle position endpoints."""
        params = {"spec": "gtfs-rt", "limit": limit}
        data = self._request("feeds", params)
        feeds = data.get("feeds", [])
        rt_feeds = []
        for f in feeds:
            urls = f.get("urls", {})
            vp_url = urls.get("realtime_vehicle_positions")
            if vp_url:
                rt_feeds.append({
                    "onestop_id": f.get("onestop_id"),
                    "name": f.get("name") or f.get("onestop_id"),
                    "vehicle_positions_url": vp_url,
                    "trip_updates_url": urls.get("realtime_trip_updates"),
                    "alerts_url": urls.get("realtime_alerts"),
                })
        return rt_feeds

    def get_routes(self, operator_onestop_id: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch routes for a given operator or region."""
        params = {"limit": limit}
        if operator_onestop_id:
            params["operator_onestop_id"] = operator_onestop_id
        data = self._request("routes", params)
        return data.get("routes", [])


if __name__ == "__main__":
    import urllib.parse
    logging.basicConfig(level=logging.INFO)
    adapter = TransitlandAdapter()
    print("Testing Transitland operators...")
    operators = adapter.get_operators(limit=3)
    for op in operators:
        print(f"- {op.get('name')} ({op.get('onestop_id')})")
    
    print("\nTesting GTFS-RT feeds...")
    rt_feeds = adapter.get_realtime_feeds(limit=3)
    for rf in rt_feeds:
        print(f"- {rf['onestop_id']} -> {rf['vehicle_positions_url']}")
