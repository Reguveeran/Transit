# Normalized Transport Event Specification

**Schema Name**: `transport.event.v1`  
**MIME Type**: `application/vnd.unitransit.event.v1+json`  

---

## 1. Schema Definition

| Field | Type | Required | Description | Constraints / Examples |
|---|---|---|---|---|
| `event_id` | `UUID` (String) | Optional | Unique ID of telemetry event | Auto-generated if omitted (e.g. `c73a4b08-39d6-444a-b5e1-88f6f59c118b`) |
| `vehicle_id` | `String` | **Yes** | Unique identifier of vehicle | Alphanumeric, hyphen, underscore (e.g. `BUS-101`, `METRO-A2`) |
| `mode` | `String` | **Yes** | Transport modality | Enum: `bus`, `train`, `metro`, `tram`, `ferry`, `aircraft` |
| `route_id` | `String` | **Yes** | Associated route ID | e.g. `ROUTE-12` |
| `trip_id` | `String` | Optional | Scheduled active trip ID | e.g. `TRIP-2026-0919-M1` |
| `latitude` | `Float` | **Yes** | Latitude in decimal degrees | `-90.0` to `90.0` |
| `longitude` | `Float` | **Yes** | Longitude in decimal degrees | `-180.0` to `180.0` |
| `speed` | `Float` | **Yes** | Vehicle speed in km/h | `>= 0.0` (e.g. `45.2`) |
| `heading` | `Float` | **Yes** | Compass bearing in degrees | `0.0` to `360.0` (0 = North, 90 = East, 180 = South, 270 = West) |
| `status` | `String` | **Yes** | Current operational status | Enum: `SCHEDULED`, `BOARDING`, `MOVING`, `STOPPED`, `CONGESTED`, `OFFLINE`, `EMERGENCY` |
| `occupancy_status`| `String` | Optional | Vehicle passenger load | Enum: `EMPTY`, `MANY_SEATS_AVAILABLE`, `FEW_SEATS_AVAILABLE`, `STANDING_ROOM_ONLY`, `FULL`, `NOT_ACCEPTING_PASSENGERS` |
| `delay_seconds` | `Integer` | Optional | Current delay against schedule | Defaults to `0` (positive = late, negative = early) |
| `timestamp` | `ISO 8601 String` | **Yes** | UTC event observation time | e.g. `2026-09-19T18:30:00Z` |

---

## 2. Canonical JSON Sample

```json
{
  "event_id": "c73a4b08-39d6-444a-b5e1-88f6f59c118b",
  "vehicle_id": "BUS-101",
  "mode": "bus",
  "route_id": "ROUTE-12",
  "trip_id": "TRIP-2026-0919-01",
  "latitude": 12.9716,
  "longitude": 80.2440,
  "speed": 42.5,
  "heading": 180.0,
  "status": "MOVING",
  "occupancy_status": "MANY_SEATS_AVAILABLE",
  "delay_seconds": 45,
  "timestamp": "2026-09-19T18:30:00Z"
}
```
