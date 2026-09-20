# UniTransit AWS EKS Workload Deployment & Architecture Guide

## 1. Executive Summary & Progression

```text
Phase 9.1: Modular Terraform Multi-Environment Architecture         ✅
Phase 9.2: Container Supply Chain & Immutable Digest Pinning         ✅
Phase 9.3A: AWS VPC, Subnetting, Security Groups & IAM Roles         ✅
Phase 9.3B: AWS EKS Control Plane & Managed Node Groups Architecture ✅
Phase 9.3C: AWS RDS PostgreSQL (PostGIS) & ElastiCache Redis Tier    ✅
Phase 9.3D: UniTransit Stateless Workloads Deployment on EKS         ✅ (Current)
Phase 9.3E: AWS Load Balancer Controller, Ingress, TLS & DNS        ← (Next)
```

---

## 2. Stateless Compute Architecture on EKS

In Phase 9.3D, all stateful persistence and caching remain strictly outside the Kubernetes compute cluster on managed AWS services (RDS PostgreSQL with PostGIS in Private DB Subnets and ElastiCache Redis in Private DB Subnets). EKS hosts only stateless, horizontally-scalable application tiers.

```text
                           Internet (Future ALB Ingress - Phase 9.3E)
                                              │
                    ┌─────────────────────────┴─────────────────────────┐
                    │            AWS EKS Cluster (Kubernetes v1.30)     │
                    │               Namespace: unitransit-dev / prod    │
                    │                                                   │
                    │   ┌───────────────────────────────────────────┐   │
                    │   │               Frontend Tier               │   │
                    │   │    • React Production Nginx Service       │   │
                    │   │    • Port 80 (ClusterIP: frontend-service)│   │
                    │   └─────────────────────┬─────────────────────┘   │
                    │                         │                         │
                    │   ┌─────────────────────▼─────────────────────┐   │
                    │   │            Backend API / ASGI             │   │
                    │   │    • Daphne ASGI (HTTP + WebSocket)       │   │
                    │   │    • Probes: /health (live), /ready (rdt) │   │
                    │   │    • Port 8000 (backend-service)          │   │
                    │   └──────┬──────────────────────┬─────────────┘   │
                    │          │                      │                 │
                    │   ┌──────▼──────┐        ┌──────▼──────┐          │
                    │   │PositionWorkr│        │ AlertWorker │          │
                    │   │(Stream Cons)│        │(Notification│          │
                    │   └──────┬──────┘        └──────┬──────┘          │
                    └──────────┼──────────────────────┼─────────────────┘
                               │                      │
                        Port 5432 (TLS)        Port 6379 (TLS)
                        Strict SG Rule         Strict SG Rule
                               │                      │
                               ▼                      ▼
                ┌──────────────────────┐┌──────────────────────┐
                │    AWS RDS PostGIS   ││ AWS ElastiCache Redis│
                │ • PostgreSQL 15.7    ││ • Redis 7.1 Engine   │
                │ • Spatial Extensions ││ • transport.events   │
                │ • Multi-AZ (Prod)    ││ • unitransit_workers │
                │ (Private DB Subnets) ││ (Private DB Subnets) │
                └──────────────────────┘└──────────────────────┘
```

---

## 3. Workload Deployment Specifications (`terraform/aws/modules/workloads/`)

### A. Controlled Database Migration & PostGIS Validation Job (`unitransit-db-migrate`)
- **Execution**: Runs `python manage.py migrate --noinput` as a Kubernetes Job with `backoff_limit = 3`.
- **Spatial Validation**: Executes a live check against PostgreSQL verifying `SELECT PostGIS_Version();` before backend or worker pods start receiving traffic.
- **Safety**: Prevents concurrent migration race conditions across backend replicas.

### B. Backend API Tier (`backend`)
- **Server**: Daphne ASGI Server supporting synchronous REST endpoints, Django Channels real-time WebSockets, and Prometheus `/metrics`.
- **Probes**:
  - `startupProbe`: `GET /health` (failure threshold 10, period 5s)
  - `livenessProbe`: `GET /health` (initial delay 15s, period 10s)
  - `readinessProbe`: `GET /ready` (verifies active RDS PostgreSQL & ElastiCache connections; period 5s)
- **Zero-Downtime Updates**: RollingUpdate with `max_surge = 1` and `max_unavailable = 0`.

### C. Stream Processing Workers (`worker-position` & `worker-alert`)
- **PositionWorker**:
  - Stream Target: `transport.events`
  - Consumer Group: `unitransit_workers`
  - Contract: Non-destructive acknowledgment (`XACK`), poison-pill dead-letter isolation, pending entry list (PEL) recovery, and automated claim (`XAUTOCLAIM`).
- **AlertWorker**: Subscribes to telemetry breach events and dispatches notifications.

### D. Frontend Web Tier (`frontend`)
- **Stack**: React Single-Page Application served via optimized Nginx container.
- **Probes**: `GET /` on port 80.

---

## 4. Immutable Container Artifact References

All workloads deploy immutable image artifacts published to GitHub Container Registry (`ghcr.io`) without rebuilding:

| Component | Dev Environment (Git SHA Pin) | Prod Environment (Cryptographic SHA-256 Digest) |
| :--- | :--- | :--- |
| **Backend** | `ghcr.io/reguveeran/unitransit-backend:8916745` | `ghcr.io/reguveeran/unitransit-backend@sha256:7be9f178dfdb211b8f14acde4ffcf3665a3c051261cb2841accd06c9a38541e2` |
| **Workers** | `ghcr.io/reguveeran/unitransit-worker:8916745` | `ghcr.io/reguveeran/unitransit-worker@sha256:7be9f178dfdb211b8f14acde4ffcf3665a3c051261cb2841accd06c9a38541e2` |
| **Frontend** | `ghcr.io/reguveeran/unitransit-frontend:8916745` | `ghcr.io/reguveeran/unitransit-frontend@sha256:e9649216e17ad342130fffa0014ad3eb2ba3473ba772e293a38a7c29be0ecf62` |

---

## 5. Runtime Environment Variable Injection Matrix

| Variable | Dev / Local Target | AWS Cloud EKS Target (Decoupled Wiring) |
| :--- | :--- | :--- |
| `POSTGRES_HOST` | `postgres-service` | `module.rds.db_address` |
| `POSTGRES_PORT` | `5432` | `5432` |
| `POSTGRES_DB` | `unitransit` | `unitransit` |
| `POSTGRES_USER` | `unitransit` | `unitransit_admin` |
| `POSTGRES_PASSWORD` | `<k8s-secret>` | `<k8s-secret (sensitive tfvar)>` |
| `REDIS_HOST` | `redis-service` | `module.elasticache.primary_endpoint_address` |
| `REDIS_PORT` | `6379` | `6379` |
| `REDIS_STREAM_KEY` | `transport.events` | `transport.events` |
| `DJANGO_SETTINGS_MODULE` | `config.settings` | `config.settings` |
| `PROMETHEUS_METRICS_ENABLED`| `True` | `True` |

---

## 6. Sizing & Resource Allocations

| Workload | Dev Replicas / Requests / Limits | Prod Replicas / Requests / Limits |
| :--- | :--- | :--- |
| **Backend** | 1 replica (100m CPU, 128Mi RAM / 500m CPU, 512Mi RAM) | 3 replicas (250m CPU, 512Mi RAM / 1000m CPU, 1Gi RAM) |
| **PositionWorker** | 1 replica (100m CPU, 128Mi RAM / 250m CPU, 256Mi RAM) | 2 replicas (200m CPU, 256Mi RAM / 500m CPU, 512Mi RAM) |
| **AlertWorker** | 1 replica (100m CPU, 128Mi RAM / 250m CPU, 256Mi RAM) | 2 replicas (200m CPU, 256Mi RAM / 500m CPU, 512Mi RAM) |
| **Frontend** | 1 replica (50m CPU, 64Mi RAM / 100m CPU, 128Mi RAM) | 2 replicas (100m CPU, 128Mi RAM / 200m CPU, 256Mi RAM) |

---

## 7. Protected Local Baseline & Safety

- Local Docker Desktop Kubernetes namespaces (`unitransit`, `unitransit-iac`, `unitransit-dev`) remain active and unaffected.
- Full regression test suite: **77/77 tests passing**.
- Zero AWS resources were created or billed during this architecture and validation phase.
