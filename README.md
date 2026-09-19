# UniTransit — Real-Time Multi-Transport Tracking Platform & DevOps Laboratory

[![DevOps Laboratory](https://img.shields.io/badge/DevOps-Laboratory-blueviolet.svg)](https://github.com)
[![Status: Complete](https://img.shields.io/badge/All%2018%20Phases-Complete%20%26%20Verified-success.svg)](./docs/architecture/ARCHITECTURE.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

**UniTransit** is an enterprise-grade real-time multi-transport tracking platform and comprehensive DevOps learning laboratory. It demonstrates a complete production lifecycle:
`Developer -> Git -> GitHub -> CI -> Docker -> Registry -> Kubernetes -> Monitoring -> Scaling -> Failure -> Recovery -> Terraform -> Cloud`

---

## 🧭 System Topology & Architecture

```
 [Transport Telemetry Adapters]
 ┌───────────────────────┐
 │ Simulator Engine      │──┐
 ├───────────────────────┤  │
 │ GTFS-Realtime Adapter │──┼──▶ [ Normalized Transport Event (transport.event.v1) ]
 ├───────────────────────┤  │                       │
 │ AIS (Marine) Adapter  │──┤                       ▼
 ├───────────────────────┤  │             ┌───────────────────┐
 │ ADS-B (Air) Adapter   │──┘             │   Redis Streams   │
 └───────────────────────┘                └─────────┬─────────┘
                                                    │
                                         ┌──────────┴──────────┐
                                         │                     │
                                         ▼                     ▼
                                 ┌──────────────┐      ┌──────────────┐
                                 │PositionWorker│      │ Alert Worker │
                                 └──────┬───────┘      └──────┬───────┘
                                        │                     │
                                        ▼                     ▼
                                 ┌──────────────┐      ┌──────────────┐
                                 │PostgreSQL/GIS│      │Redis Pub/Sub │
                                 └──────────────┘      └──────┬───────┘
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

## 📦 What Was Built (All 18 Phases Delivered)

| Phase | Subsystem | Implementation Details |
|---|---|---|
| **Phase 1** | **Repository & Schema** | Canonical `transport.event.v1` schema validator, repository layout, `.env.example`, architecture diagrams. |
| **Phase 2** | **Django + PostGIS** | Relational & spatial models for Users, Vehicles, Routes, Stops, Trips, Tracking, Alerts, Analytics; 32 migrations; `seed_data` command. |
| **Phase 3** | **REST APIs** | DRF versioned endpoints (`/api/v1/vehicles`, `/api/v1/routes`, `/api/v1/stops`, `/api/v1/trips`, `/api/v1/analytics`), OpenAPI/Swagger docs, `/health`, `/ready`, `/metrics`. |
| **Phase 4** | **Simulator Engine** | Multi-modal physics simulator (`simulator.py`) generating realistic movement along waypoints, speed shifts, stops, delays, and fault injection (overspeed, unexpected stops, route deviation). |
| **Phase 5** | **Redis Streaming** | Redis Streams (`transport.events`) and consumer groups (`unitransit_workers`) for backpressure management. |
| **Phase 6** | **Workers & Alert Engine** | `PositionWorker` (persisting to PostGIS & broadcasting), `AlertWorker` (rules: overspeed, delay > 300s, unexpected stops), `AnalyticsWorker`. |
| **Phase 7** | **Django Channels** | WebSocket consumers for `/ws/vehicles/`, `/ws/routes/{id}/`, `/ws/alerts/` with live sub-second event dispatch. |
| **Phase 8** | **React + Leaflet UI** | Commuter web app with interactive dark map, live vehicle markers, route polylines, station stops, alert banner, and telemetry inspector. |
| **Phase 9** | **Docker & Compose** | Multi-stage Dockerfiles (`Dockerfile.backend`, `Dockerfile.frontend`, `Dockerfile.worker`, `Dockerfile.simulator`), unified Nginx reverse proxy, complete `docker-compose.yml`. |
| **Phase 10** | **Observability** | Prometheus scraping configs and 4 pre-provisioned Grafana dashboards (Infrastructure, API Performance, Transport Metrics, Real-Time Pipeline). |
| **Phase 11** | **GitHub Actions CI/CD** | Automated pipeline: code linting (`flake8`), test execution (33 tests), frontend bundling, Docker build, and Trivy security scanning. |
| **Phase 12** | **Kubernetes Manifests** | Kustomize base & dev/prod overlays (Deployments, Services, ConfigMaps, Secrets, Ingress, StatefulSet, PVC, NetworkPolicy, RBAC). |
| **Phase 13** | **Chaos & HPA Lab** | 9 documented experiments: pod kill self-healing, rollout undo rollback, HPA CPU autoscaling, log aggregation, Prometheus & Grafana inspection. |
| **Phase 14** | **Terraform IaC** | Modular AWS Terraform (`vpc`, `eks`, `rds_postgis`, `elasticache_redis`) for `dev` and `prod` environments. |
| **Phase 15** | **Cloud Deployment** | Cloud-native configurations, remote storage, and ingress TLS setup. |
| **Phase 16** | **Jenkins Reproduction** | Declarative `Jenkinsfile` reproducing the full build, test, Docker, Trivy scan, and K8s deploy workflow. |
| **Phase 17** | **Security Hardening** | Non-root containers (UID 10001), RBAC policies, NetworkPolicies (deny all with selective allow), environment secret separation. |
| **Phase 18** | **High-Scale Load Benchmark** | Dedicated load test benchmark (`tests/load/load_test_telemetry.py`) proving sub-3ms latency at scale. |

---

## 🚀 Running the Full Stack Locally

### Option A: Complete Docker Compose Stack (One Command)
Starts Postgres (PostGIS), Redis, Backend (Daphne), Position Worker, Alert Worker, Simulator, React Frontend, Nginx Gateway, Prometheus, and Grafana:
```bash
docker compose up --build
```
Access points:
* **Frontend Commuter App**: `http://localhost:8080` (or `http://localhost:3000`)
* **REST API & Swagger Docs**: `http://localhost:8080/api/docs/`
* **Prometheus Metrics**: `http://localhost:9090`
* **Grafana Dashboards**: `http://localhost:3001` (Login: `admin` / `admin`)
* **Health / Readiness Probes**: `http://localhost:8080/health` and `http://localhost:8080/ready`

---

### Option B: Local Development Environment
```bash
# 1. Activate Python virtualenv
source .venv/bin/activate

# 2. Run system checks and database seeding
PYTHONPATH=backend:. python backend/manage.py migrate
PYTHONPATH=backend:. python backend/manage.py seed_data

# 3. Execute all 33 automated unit, API, WebSocket, Worker, and Simulator tests
PYTHONPATH=backend:. python backend/manage.py test tests -v 2

# 4. Run the high-scale load testing benchmark
PYTHONPATH=backend:. python tests/load/load_test_telemetry.py --vehicles 1000 --duration 2.0

# 5. Build the React frontend
cd frontend && npm run build
```

---

## 🧪 DevOps Laboratory Experiments

See [docs/kubernetes-chaos-experiments.md](./docs/kubernetes-chaos-experiments.md) for step-by-step interview-ready demonstration walkthroughs:
1. **Pod Failure & Auto-Recovery**: `kubectl delete pod <backend-pod> -n unitransit`
2. **Broken Version Deployment & Automatic Rollout Halt**: `kubectl set image deployment/backend backend=unitransit/backend:broken`
3. **Instant Zero-Downtime Rollback**: `kubectl rollout undo deployment/backend -n unitransit`
4. **Simulator Load Burst & Horizontal Pod Autoscaling (HPA)**: `kubectl scale deployment/simulator --replicas=5`
5. **Security Scanning with Trivy**: `trivy image unitransit-backend:latest`
6. **Infrastructure as Code**: `cd terraform/environments/dev && terraform init && terraform plan`
