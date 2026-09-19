# Event Workers

Stateless consumer workers that pull events from Redis Stream `transport.events` via Redis Consumer Groups (`unitransit_workers`).

## Workers
1. `position_worker/`: Batch-persists telemetry into PostGIS `vehicle_positions` table and publishes real-time coordinate updates to Redis Pub/Sub (`vehicle.updates`).
2. `alert_worker/`: Evaluates events against business alert rules (overspeed, route deviation, unexpected stop, offline detection) and dispatches alerts to Redis Pub/Sub (`alerts`).
3. `analytics_worker/`: Periodically aggregates delay statistics, speed averages, and transit performance metrics.
