# Observability & Monitoring

Prometheus and Grafana configurations for real-time observability across the UniTransit platform.

## Dashboards
1. **Infrastructure**: CPU, memory, container restarts, host disk and network I/O.
2. **API Performance**: Request rate, p95/p99 latency, HTTP status code distribution (2xx, 4xx, 5xx).
3. **Transport Metrics**: Active vehicles per mode, average speeds, delay distribution, alerts generated.
4. **Real-time Pipeline**: Redis Stream length, consumer lag, events processed/sec, WebSocket active connections.
