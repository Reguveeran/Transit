# UniTransit — Real-Time Multi-Transport Tracking Platform

[![DevOps Laboratory](https://img.shields.io/badge/DevOps-Laboratory-blueviolet.svg)](https://github.com)
[![Status: Phase 1 Active](https://img.shields.io/badge/Phase%201-Architecture%20Blueprint-success.svg)](./docs/architecture/ARCHITECTURE.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

**UniTransit** is an enterprise-grade, real-time multi-transport tracking platform and comprehensive DevOps learning laboratory. Designed from first principles to decouple transport telemetry ingestion from storage, analytics, and client visualization, it provides live tracking for buses, trains/metros, ferries, and aircraft through a unified normalized event bus.

---

## 🧭 Architectural Overview

```
 [Transport Adapters]
 ┌───────────────────────┐
 │ Simulator Engine      │──┐
 ├───────────────────────┤  │
 │ GTFS-Realtime Adapter │──┼──▶ [ Normalized Transport Event ]
 ├───────────────────────┤  │             │
 │ AIS (Marine) Adapter  │──┤             ▼
 ├───────────────────────┤  │    ┌─────────────────┐
 │ ADS-B (Air) Adapter   │──┘    │  Redis Streams  │
 └───────────────────────┘       └────────┬────────┘
                                          │
                                 ┌────────┴────────┐
                                 │                 │
                                 ▼                 ▼
                         ┌──────────────┐  ┌──────────────┐
                         │PositionWorker│  │ Alert Worker │
                         └──────┬───────┘  └──────┬───────┘
                                │                 │
                                ▼                 ▼
                         ┌──────────────┐  ┌──────────────┐
                         │PostgreSQL/GIS│  │Redis Pub/Sub │
                         └──────────────┘  └──────┬───────┘
                                                  │
                                                  ▼
                                           ┌──────────────┐
                                           │DjangoChannels│
                                           │ (WebSockets) │
                                           └──────┬───────┘
                                                  │
                                                  ▼
                                           ┌──────────────┐
                                           │React Leaflet │
                                           │  Frontend UI │
                                           └──────────────┘
```

---

## 📂 Repository Structure

```
unitransit/
├── frontend/               # React + Leaflet interactive commuter live map
├── backend/                # Django, Django REST Framework, Django Channels
│   ├── apps/
│   │   ├── users/          # Authentication & User Preferences
│   │   ├── vehicles/       # Vehicle registry & metadata
│   │   ├── routes/         # Transit routes & geometric polyline paths
│   │   ├── stops/          # Geo-located stops & estimated arrivals
│   │   ├── trips/          # Scheduled & active transit trips
│   │   ├── tracking/       # Live telemetry & spatial queries
│   │   ├── alerts/         # Service alerts & rule violations
│   │   └── analytics/      # Historical performance & delay aggregation
│   └── common/             # Logging, metrics, exceptions, middlewares
├── adapters/               # Telemetry ingestion adapters producing normalized events
│   ├── common/             # Normalized event schemas & validators
│   ├── simulator/          # High-performance multi-modal vehicle simulator
│   ├── gtfs_realtime/      # GTFS-RT protocol buffer adapter
│   ├── ais/                # Marine automatic identification system adapter
│   └── adsb/               # Aviation ADS-B telemetry adapter
├── workers/                # Scalable background event consumer workers
│   ├── position_worker/    # Persists telemetry into PostGIS & broadcasts updates
│   ├── alert_worker/       # Evaluates overspeed, route deviation, stopped rules
│   └── analytics_worker/   # Computes aggregate delays & stats
├── monitoring/             # Observability configurations
│   ├── prometheus/         # Scrape configs & alert rules
│   └── grafana/            # Pre-configured dashboards (Infra, API, Realtime)
├── k8s/                    # Kubernetes production manifests (Base & Overlays)
├── terraform/              # Infrastructure as Code (EKS/GKE cloud environments)
├── docker/                 # Production-grade multi-stage Dockerfiles
├── tests/                  # Unit, integration, and end-to-end test suites
├── docs/                   # System architecture & DevOps lab guides
├── .github/workflows/      # Automated CI/CD pipelines & Trivy security scanning
├── docker-compose.yml      # Local single-command development environment
└── Jenkinsfile             # Declarative Jenkins CI/CD pipeline
```

---

## 🚦 Normalized Event Specification

Every transport source (simulator, GTFS-RT, AIS, ADS-B) is normalized into a strict canonical schema:

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "vehicle_id": "BUS-101",
  "mode": "bus",
  "route_id": "ROUTE-12",
  "trip_id": "TRIP-20260919-01",
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

---

## 🛠️ Multi-Phase DevOps Learning Path

1. **Phase 1**: Repository structure & Architecture Blueprint *(Completed)*
2. **Phase 2**: Django + PostgreSQL + PostGIS Core Models
3. **Phase 3**: Vehicle, Route, Stop, Trip REST APIs & Spatial Queries
4. **Phase 4**: High-Load Transport Simulator Engine
5. **Phase 5**: Redis Event Streaming Pipeline (Streams & Consumer Groups)
6. **Phase 6**: Scalable Event Workers & Real-Time Alert Engine
7. **Phase 7**: Django Channels WebSockets & Live Broadcast
8. **Phase 8**: React + Leaflet Interactive Live Map
9. **Phase 9**: Docker & Multi-Container Docker Compose Stack
10. **Phase 10**: Prometheus Metrics & Grafana Observability Dashboards
11. **Phase 11**: GitHub Actions CI/CD Pipeline & Trivy Vulnerability Scans
12. **Phase 12**: Kubernetes Manifests (Deployments, Ingress, NetworkPolicies)
13. **Phase 13**: Kubernetes Chaos, Rollback & HPA Autoscaling Experiments
14. **Phase 14**: Terraform Infrastructure as Code (Cloud Modules)
15. **Phase 15**: Cloud Deployment Verification
16. **Phase 16**: Jenkins Declarative Pipeline Reproduction
17. **Phase 17**: Security Hardening & Zero-Trust Policies
18. **Phase 18**: High-Scale Load Testing (10,000+ Concurrent Vehicles)

---

## 🚀 Getting Started (Phase 1)

### Requirements
- Python 3.10+
- `pytest` for running unit test suites

### Run Event Schema Validation Tests
```bash
python3 -m unittest discover -s tests
```
