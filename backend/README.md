# Backend Modules

This directory contains the Django / Django REST Framework / Django Channels backend service.

## Structure
- `core/`: Django settings, ASGI/WSGI entry points, URL root router.
- `apps/users/`: Authentication, user profiles, and commuter preferences.
- `apps/vehicles/`: Transport vehicle registry, operational states, and metadata.
- `apps/routes/`: Transit routes, geometries, lines, and shape files.
- `apps/stops/`: Geocoded transit stations/stops and estimated arrival schedules.
- `apps/trips/`: Trip schedules, runs, and active journeys.
- `apps/tracking/`: Telemetry positions, PostGIS spatial queries, and live map feeds.
- `apps/alerts/`: Service alerts, delays, and incident management.
- `apps/analytics/`: Historical transit statistics, delay histograms, and aggregations.
- `common/`: Shared middleware, metrics interceptors, standard responses, and error handlers.
