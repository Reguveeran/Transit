# UniTransit Real-Time Data Flow & Message Pipeline

## 1. End-to-End Telemetry Lifecycle

```mermaid
sequenceDiagram
    autonumber
    participant Adapter as Transport Adapter (Simulator/GTFS/AIS)
    participant RedisStream as Redis Stream (transport.events)
    participant Worker as Telemetry Worker Pool
    participant DB as PostgreSQL + PostGIS
    participant RedisPub as Redis Pub/Sub (vehicle.updates)
    participant WS as Django Channels Gateway
    participant UI as React Leaflet Client

    Adapter->>Adapter: Normalize raw source data into transport.event.v1
    Adapter->>RedisStream: XADD transport.events * payload (JSON)
    RedisStream->>Worker: XREADGROUP GROUP unitransit_workers
    
    par Persistence (Warm Path)
        Worker->>DB: INSERT INTO vehicle_positions (ST_SetSRID(ST_MakePoint(...), 4326))
        Worker->>DB: UPDATE vehicles SET current_location, last_seen
    and Realtime Broadcast (Hot Path)
        Worker->>RedisPub: PUBLISH vehicle.updates {vehicle_id, lat, lon, speed, heading}
    end

    RedisPub->>WS: Broadcast to connected channel groups
    WS->>UI: WebSocket frame {type: "vehicle.position_update", ...}
    UI->>UI: Update vehicle marker position smoothly with Leaflet
    Worker->>RedisStream: XACK transport.events unitransit_workers <msg_id>
```

---

## 2. Ingestion Guarantees & Error Handling

- **At-least-once delivery**: Workers acknowledge processed stream items with `XACK`. Unacknowledged messages are reclaimed via `XAUTOCLAIM` if a worker crashes.
- **Deduplication**: `event_id` or `(vehicle_id, timestamp)` acts as the idempotency key in the PostGIS storage layer.
- **Backpressure**: Redis stream maximum length (`MAXLEN ~ 50000`) prevents memory exhaustion during subscriber downtime.
