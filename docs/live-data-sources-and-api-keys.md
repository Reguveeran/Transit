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
* **API Credentials**:
  * **OpenSky OAuth2 API Client (Connected)**: Create a client at OpenSky user profile -> API Clients.
* **Configuration in `.env`**:
  ```env
  ENABLE_OPENSKY=true
  OPENSKY_CLIENT_ID=reguveeran-api-client
  OPENSKY_CLIENT_SECRET=xccjMwc8m07D6BHext9lImHAq61amgBF
  ```
* **Adapter Script**: `adapters/adsb/opensky_adapter.py`
* **OAuth2 Authentication**: Exchanges `clientId` and `clientSecret` for a JWT Bearer token with Keycloak at `https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token`.

---

### B. Live Public Transit (Buses & Metro - Transitland v2 & GTFS-Realtime)
* **Provider**: [Transitland v2 REST API](https://transit.land/) (Interline Technologies)
* **Cost**: **Free Developer Tier**
* **Status**: **Connected & Verified**
* **Configuration in `.env`**:
  ```env
  ENABLE_TRANSITLAND=true
  TRANSITLAND_API_KEY=iwa_live_tlv2api_5dca056029ec20f4573e86706f49b9143e01554be166d8dd3ABHBj
  ```
* **Adapter Script**: `adapters/gtfs_realtime/transitland_adapter.py`
* **Features**:
  * Auto-discovers transit operators, routes, and active GTFS-Realtime vehicle position feeds worldwide.
  * Connects directly to agency vehicle feeds (e.g. Arlington Transit, Barrie, Big Blue Bus, Burlington, Calgary Transit, NYC MTA, TfL).
  * Direct feed override (optional):
    ```env
    GTFS_RT_VEHICLE_POSITIONS_URL=https://realtime.arlingtontransit.com/gtfsrt/vehicles
    ```

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
