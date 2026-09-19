# UniTransit System Architecture Blueprint

## 1. Core Principles

1. **Decoupled Telemetry Ingestion**: The core transit backend and client layer have zero knowledge of source protocols (GTFS-RT, AIS, ADS-B, Simulator).
2. **Canonical Event Normalization**: Every incoming event must conform to `transport.event.v1` schema before entering internal queues.
3. **Event Streaming with Backpressure**: Telemetry bursts are absorbed by Redis Streams (`XADD`), processed by stateless worker pools in consumer groups (`XREADGROUP`), and persisted asynchronously.
4. **Separation of Hot vs. Warm/Cold Paths**:
   - **Hot Path**: Event -> Redis Stream -> Worker -> Redis Pub/Sub -> WebSocket Gateway -> Frontend map marker update (< 100ms latency).
   - **Warm Path**: Worker -> PostGIS `vehicle_positions` table (Spatial index for proximity queries).
   - **Cold Path**: Aggregated delays, speed histograms, route performance -> Analytics tables / Prometheus metrics.
5. **Observability First**: All components expose OpenMetrics endpoints (`/metrics`) for Prometheus scraping.

---

## 2. Component Topology

```mermaid
flowchart TD
    subgraph Ingestion["Ingestion Adapters"]
        SIM["Simulator Engine"] -->|Raw State| ADAPT_SIM["Simulator Adapter"]
        GTFS["GTFS-RT Feed"] -->|Protobuf| ADAPT_GTFS["GTFS Adapter"]
        AIS["AIS Marine Feed"] -->|NMEA 0183| ADAPT_AIS["AIS Adapter"]
        ADSB["ADS-B Feed"] -->|JSON / Mode-S| ADAPT_ADSB["ADS-B Adapter"]
    end

    subgraph Streaming["Message Bus"]
        ADAPT_SIM -->|Normalized Event| STREAM["Redis Stream\n(transport.events)"]
        ADAPT_GTFS -->|Normalized Event| STREAM
        ADAPT_AIS -->|Normalized Event| STREAM
        ADAPT_ADSB -->|Normalized Event| STREAM
    end

    subgraph Workers["Worker Services (Consumer Group: unitransit_workers)"]
        STREAM -->|Consumer 1..N| POS_W["Position Worker"]
        STREAM -->|Consumer 1..N| ALERT_W["Alert Worker\n(Rule Engine)"]
        STREAM -->|Consumer 1..N| STATS_W["Analytics Worker"]
    end

    subgraph Storage["Datastores"]
        POS_W -->|Batch INSERT (Spatial Point)| DB[(PostgreSQL + PostGIS)]
        STATS_W -->|UPDATE Aggregates| DB
    end

    subgraph Realtime["Real-time Distribution"]
        POS_W -->|PUBLISH vehicle.updates| REDIS_PUB["Redis Pub/Sub"]
        ALERT_W -->|PUBLISH alerts| REDIS_PUB
        REDIS_PUB -->|Channel Sub| WS["Django Channels\n(WebSocket Server)"]
    end

    subgraph Clients["Presentation & Observability"]
        WS -->|Live JSON updates| UI["React + Leaflet UI"]
        DB -->|REST API (DRF)| UI
        DB -.->|Scrape| PROM["Prometheus"]
        WS -.->|Scrape| PROM
        POS_W -.->|Metrics| PROM
        PROM --> GRAF["Grafana Dashboards"]
    end
```

---

## 3. Communication Protocols

| Interface | Source | Destination | Protocol / Format | Purpose |
|---|---|---|---|---|
| Telemetry Ingest | Adapters | Redis Stream | Redis `XADD` (JSON) | High-throughput event ingestion with persistence |
| Worker Consumption | Redis Stream | Workers | Redis `XREADGROUP` | Load balanced, fault-tolerant event processing |
| Live Broadcast | Workers | Django Channels | Redis Pub/Sub | Pub/Sub routing to active WebSocket consumer channels |
| Client Realtime | Django Channels | React WebApp | WSS (WebSocket) | Sub-second vehicle marker coordinate updates |
| Client REST API | React WebApp | Django REST Framework | HTTPS (JSON) | Routes, stops, schedule, historical analytics queries |
| Observability | Prometheus | All Services | HTTP GET `/metrics` | Time-series metrics collection |
