# Telemetry Ingestion Adapters

Adapters consume telemetry from external domain-specific protocols and normalize them into the canonical `transport.event.v1` schema before pushing to Redis Streams (`transport.events`).

## Modules
- `common/`: Canonical schemas, Pydantic/dataclass models, and validation logic.
- `simulator/`: Multi-vehicle movement and GPS telemetry simulator with configurable fault rates.
- `gtfs_realtime/`: Ingestion adapter for GTFS-RT (Protocol Buffers) vehicle positions.
- `ais/`: Marine vessel Automatic Identification System (NMEA 0183 / AIS AIVDM) adapter.
- `adsb/`: Aviation ADS-B Mode-S telemetry adapter.
