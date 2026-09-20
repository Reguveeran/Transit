# UniTransit Phase 9.1: Modular Terraform Migration Plan

## 1. Current Phase 8 Terraform Inventory (`terraform/k8s/`)

The Phase 8 implementation is a monolithic flat root module targeting the single isolated namespace `unitransit-iac`. It provisions 18 Kubernetes resources:

| Resource Type | Resource Identifier | File | Current Purpose |
| :--- | :--- | :--- | :--- |
| `kubernetes_namespace` | `unitransit_iac` | `namespace.tf` | Isolated environment namespace |
| `kubernetes_config_map` | `unitransit_config` | `config.tf` | App configuration (DB/Redis hosts, PYTHONPATH) |
| `kubernetes_secret` | `unitransit_secrets` | `config.tf` | Sensitive credentials (DB password, Django key) |
| `kubernetes_deployment` | `redis` | `redis.tf` | Redis Stream broker (1 replica, port 6379) |
| `kubernetes_service` | `redis_service` | `redis.tf` | ClusterIP service for Redis (`redis-service`) |
| `kubernetes_stateful_set` | `postgres` | `postgres.tf` | PostGIS database with 5Gi volume claim template |
| `kubernetes_service` | `postgres_service` | `postgres.tf` | ClusterIP service for PostgreSQL (`postgres-service`) |
| `kubernetes_deployment` | `backend` | `backend.tf` | Daphne ASGI server (1 replica, port 8000) |
| `kubernetes_service` | `backend_service` | `backend.tf` | ClusterIP service for Backend (`backend-service`) |
| `kubernetes_deployment` | `worker_position` | `workers.tf` | Position worker stream consumer |
| `kubernetes_deployment` | `worker_alert` | `workers.tf` | Alert worker geofence processor |
| `kubernetes_deployment` | `frontend` | `frontend.tf` | Nginx React frontend (1 replica, port 80) |
| `kubernetes_service` | `frontend_service` | `frontend.tf` | ClusterIP service for Frontend (`frontend-service`) |
| `kubernetes_config_map` | `prometheus_config` | `monitoring.tf` | Prometheus scrape configuration |
| `kubernetes_deployment` | `prometheus` | `monitoring.tf` | Prometheus telemetry server (port 9090) |
| `kubernetes_service` | `prometheus_service`| `monitoring.tf` | ClusterIP service for Prometheus (`prometheus-service`) |
| `kubernetes_deployment` | `grafana` | `monitoring.tf` | Grafana dashboard server (port 3000) |
| `kubernetes_service` | `grafana_service` | `monitoring.tf` | ClusterIP service for Grafana (`grafana-service`) |

---

## 2. Resource-to-Module Mapping

To transition from a flat manifest to a production-grade multi-environment architecture, resources are decomposed into 6 reusable modules under `terraform/modules/`:

### A. `modules/networking`
- **Scope**: Narrowly scoped to namespace and shared configuration primitives.
- **Resources**:
  - `kubernetes_namespace`
  - `kubernetes_config_map` (`unitransit-config`)
  - `kubernetes_secret` (`unitransit-secrets`)
- **Exposed Outputs**:
  - `namespace_name`: Target namespace string
  - `config_map_name`: Name of application ConfigMap
  - `secret_name`: Name of credentials Secret

### B. `modules/database`
- **Scope**: PostgreSQL with PostGIS database tier.
- **Resources**:
  - `kubernetes_stateful_set` (`postgres`)
  - `kubernetes_service` (`postgres-service`)
- **Exposed Outputs**:
  - `service_name`: ClusterIP service name (`postgres-service`)
  - `service_port`: Database port (`5432`)
  - `database_name`: Database name (`unitransit`)
  - `database_host`: Host address (`postgres-service.<namespace>.svc.cluster.local`)

### C. `modules/cache`
- **Scope**: Redis streaming message broker and caching tier.
- **Resources**:
  - `kubernetes_deployment` (`redis`)
  - `kubernetes_service` (`redis-service`)
- **Exposed Outputs**:
  - `service_name`: ClusterIP service name (`redis-service`)
  - `service_port`: Redis port (`6379`)
  - `redis_host`: Host address (`redis-service.<namespace>.svc.cluster.local`)

### D. `modules/compute`
- **Scope**: Application business logic and streaming consumers.
- **Resources**:
  - `kubernetes_deployment` (`backend`)
  - `kubernetes_service` (`backend-service`)
  - `kubernetes_deployment` (`worker-position`)
  - `kubernetes_deployment` (`worker-alert`)
- **Exposed Outputs**:
  - `backend_service_name`: ClusterIP service name (`backend-service`)
  - `backend_service_port`: Backend HTTP port (`8000`)
  - `worker_deployments`: List of worker deployment names

### E. `modules/frontend`
- **Scope**: User interface static asset web tier.
- **Resources**:
  - `kubernetes_deployment` (`frontend`)
  - `kubernetes_service` (`frontend-service`)
- **Exposed Outputs**:
  - `frontend_service_name`: ClusterIP service name (`frontend-service`)
  - `frontend_service_port`: Frontend HTTP port (`80`)

### F. `modules/monitoring`
- **Scope**: Observability and telemetry stack.
- **Resources**:
  - `kubernetes_config_map` (`prometheus-config`)
  - `kubernetes_deployment` (`prometheus`)
  - `kubernetes_service` (`prometheus-service`)
  - `kubernetes_deployment` (`grafana`)
  - `kubernetes_service` (`grafana-service`)
- **Exposed Outputs**:
  - `prometheus_service_name`: Prometheus service name
  - `grafana_service_name`: Grafana service name

---

## 3. Module Dependency Graph

```text
                  networking
                 (Namespace, Config, Secrets)
                      │
           ┌──────────┴──────────┐
           ▼                     ▼
        database               cache
      (PostgreSQL)            (Redis)
           │                     │
           └──────────┬──────────┘
                      ▼
                   compute ◄──────── frontend
           (Backend & Workers)       (Web UI)
                      │
                      ▼
                  monitoring
             (Prometheus & Grafana)
```

1. **`networking`** initializes the namespace, application ConfigMap, and Secrets.
2. **`database`** and **`cache`** depend on `networking` (they mount ConfigMap and Secrets for credentials).
3. **`compute`** depends on `database`, `cache`, and `networking` (backend and workers query PostgreSQL and stream via Redis).
4. **`frontend`** operates independently inside the namespace.
5. **`monitoring`** scrapes `compute` (`backend-service:8000/metrics`) inside the namespace.

---

## 4. Environment-Specific Parameter Matrix

| Parameter | Dev (`unitransit-dev`) | Staging (`unitransit-staging`) | Prod (`unitransit-prod`) |
| :--- | :--- | :--- | :--- |
| **Namespace** | `unitransit-dev` | `unitransit-staging` | `unitransit-prod` |
| **Backend Replicas** | `1` | `2` | `3` |
| **Position Worker Replicas**| `1` | `2` | `3` |
| **Alert Worker Replicas** | `1` | `1` | `2` |
| **Frontend Replicas** | `1` | `2` | `3` |
| **Backend CPU Request / Limit** | `100m` / `1000m` | `200m` / `1000m` | `500m` / `2000m` |
| **Backend Mem Request / Limit** | `128Mi` / `1Gi` | `256Mi` / `1Gi` | `512Mi` / `2Gi` |
| **Worker CPU Request / Limit** | `100m` / `500m` | `150m` / `500m` | `250m` / `1000m` |
| **Worker Mem Request / Limit** | `128Mi` / `512Mi` | `256Mi` / `512Mi` | `512Mi` / `1Gi` |
| **PostgreSQL Storage** | `5Gi` | `10Gi` | `50Gi` (Future Managed RDS) |
| **Target Deployment Action** | Full Apply & Validate | Plan Only | Declaration & Plan Only |

---

## 5. State Isolation Strategy

- Each environment directory (`terraform/environments/{dev,staging,prod}`) maintains its own independent state file (`terraform.tfstate`).
- There is **zero state sharing** between environments. Applying or destroying `dev` has no impact on `staging` or `prod`.
- **Absolute Preservation Rule**:
  - `unitransit` (original Docker/Kubernetes namespace) is untouched.
  - `unitransit-iac` (Phase 8 isolated reference) has its own independent state in `terraform/k8s/terraform.tfstate` and remains untouched.
  - `unitransit-dev` has its own independent state in `terraform/environments/dev/terraform.tfstate`.
