# Connecting UniTransit to Live Real-World Data & API Keys

UniTransit is designed from first principles with **adapter decoupling**. You can feed it via:
1. **Background Built-in Simulator** (Zero API keys needed, works immediately out of the box)
2. **Real-World Live Flight Feeds (ADS-B Aircraft)**
3. **Real-World Live Public Transit Feeds (GTFS-Realtime Buses & Metro)**
4. **Real-World Live Maritime Feeds (AIS Ships & Ferries)**

---

## 1. Zero-Key Instant Live Background Streaming

If you want live real-time vehicle movement without signing up for external APIs, the built-in background stream is already running:

```bash
# Run continuous background telemetry updates (20 vehicles moving live across routes)
PYTHONPATH=backend:. ./.venv/bin/python backend/manage.py run_live_stream --vehicles 20 --interval 2.0
```

---

## 2. API Keys & Feeds for Real Live Data

### A. Live Aircraft Tracking (ADS-B Aviation)
* **Provider**: [The OpenSky Network](https://opensky-network.org/)
* **Cost**: **Free** (Open community data)
* **API Key / Credentials**:
  * **Anonymous Access**: No API key required! You can make requests every 10 seconds for free.
  * **Registered Account** (Optional for higher limits): Free account signup at [opensky-network.org/my-opensky](https://opensky-network.org/my-opensky).
* **Configuration in `.env`**:
  ```env
  OPENSKY_USERNAME=your_free_username
  OPENSKY_PASSWORD=your_password
  ```
* **Adapter Script**: `adapters/adsb/opensky_adapter.py`

---

### B. Live Public Transit (Buses & Metro - GTFS-Realtime)
* **Provider**: Your local city or national transit agency (e.g. NYC MTA, London TfL, MBTA, Paris RATP, Delhi Metro, Chennai MTC, Transport for NSW).
* **Cost**: **Free** for developers.
* **How to get keys**:
  1. **New York MTA**: Register free at [api.mta.info](https://api.mta.info/) -> Receive an MTA API Key.
  2. **London Transport (TfL)**: Register free at [api.tfl.gov.uk](https://api.tfl.gov.uk/) -> Receive `app_key`.
  3. **Boston MBTA**: Register free at [api-v3.mbta.com](https://api-v3.mbta.com/) -> Receive API key.
  4. **OpenMobilityData / Transitland**: Register free at [transit.land](https://www.transit.land/) -> Receive `transitland_api_key`.
* **Configuration in `.env`**:
  ```env
  GTFS_RT_VEHICLE_POSITIONS_URL=https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs
  GTFS_RT_API_KEY=your_transit_agency_api_key
  ```
* **Adapter Script**: `adapters/gtfs_realtime/gtfs_rt_adapter.py`

---

### C. Live Marine Vessels & Ferries (AIS Marine)
* **Provider**: [AISHub](https://www.aishub.net/api) or [MarineTraffic](https://www.marinetraffic.com/en/ais-api-services)
* **Cost**: Free tier for AISHub upon registering.
* **How to get key**: Register at [aishub.net/register](https://www.aishub.net/register).
* **Configuration in `.env`**:
  ```env
  AISHUB_USERNAME=your_aishub_username
  AISHUB_API_KEY=your_aishub_api_key
  ```
* **Adapter Script**: `adapters/ais/aishub_adapter.py`

---

### D. Map Tiles & Traffic (Optional UI Enhancement)
* **Provider**: [CARTO / OpenStreetMap](https://carto.com/) (Already configured in UniTransit for free with no key required) or [Mapbox](https://mapbox.com).
* **Configuration in `.env` (optional)**:
  ```env
  MAPBOX_ACCESS_TOKEN=pk.your_mapbox_token
  ```

---

## 3. Summary Configuration Checklist

Add these to your `.env` file whenever you wish to connect live external providers:

```env
# ==========================================
# External Live Data Providers (Optional)
# ==========================================

# 1. OpenSky Network (Live Flights) - https://opensky-network.org
OPENSKY_USERNAME=
OPENSKY_PASSWORD=

# 2. GTFS-Realtime (City Buses & Metro)
GTFS_RT_VEHICLE_POSITIONS_URL=
GTFS_RT_API_KEY=

# 3. AISHub (Live Ships & Ferries) - https://www.aishub.net
AISHUB_USERNAME=
AISHUB_API_KEY=
```
