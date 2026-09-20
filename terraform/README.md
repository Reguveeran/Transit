# UniTransit — Modular Multi-Environment Terraform Architecture

This directory contains the production-grade modular Terraform infrastructure for UniTransit.

---

## 1. Architectural Overview

```text
                 Terraform
                     │
          ┌──────────┼──────────┐
          │          │          │
         dev      staging      prod
          │          │          │
          └──────────┼──────────┘
                     │
              Reusable Modules
                     │
      ┌──────────────┼──────────────┐
      │       │       │      │      │
  networking database cache compute monitoring
                     │
                 frontend
```

---

## 2. Why Modules & Environment Roots Exist

- **Reusable Modules (`terraform/modules/`)**: Encapsulate resource topologies (networking primitives, database StatefulSet, Redis cache, Daphne backend & Celery/stream workers, React frontend, Prometheus & Grafana monitoring). Modules contain **zero hardcoded environment parameters** or replica counts; they accept inputs and export outputs.
- **Environment Roots (`terraform/environments/{dev,staging,prod}`)**: Compose the reusable modules and inject environment-specific configuration (replica counts, CPU/memory limits, storage size, namespaces, and credentials).
- **Difference between Module and Environment**:
  - A *module* defines **what** gets built and **how** components wire together.
  - An *environment root* defines **where**, **at what scale**, and **with what configuration** the infrastructure is instantiated.

---

## 3. Environment Specifications

| Dimension | Dev (`unitransit-dev`) | Staging (`unitransit-staging`) | Prod (`unitransit-prod`) |
| :--- | :--- | :--- | :--- |
| **Target Cluster** | Local Docker Desktop | Local Docker Desktop / Staging K8s | Production K8s Cluster |
| **Namespace** | `unitransit-dev` | `unitransit-staging` | `unitransit-prod` |
| **Backend Replicas** | 1 | 2 | 3 |
| **Position Worker Replicas** | 1 | 2 | 3 |
| **Alert Worker Replicas** | 1 | 1 | 2 |
| **Frontend Replicas** | 1 | 2 | 3 |
| **Backend CPU (Req / Lim)** | `25m` / `1000m` | `200m` / `1000m` | `500m` / `2000m` |
| **Backend Mem (Req / Lim)** | `32Mi` / `1Gi` | `256Mi` / `1Gi` | `512Mi` / `2Gi` |
| **Worker CPU (Req / Lim)** | `25m` / `500m` | `150m` / `500m` | `250m` / `1000m` |
| **Worker Mem (Req / Lim)** | `32Mi` / `512Mi` | `256Mi` / `512Mi` | `512Mi` / `1Gi` |
| **PostgreSQL Storage** | 5Gi PVC | 10Gi PVC | 50Gi (Future Managed RDS) |
| **State File** | `dev/terraform.tfstate` | `staging/terraform.tfstate` | `prod/terraform.tfstate` |

---

## 4. State Isolation Strategy

- Each environment directory maintains its own independent state file.
- **Zero state sharing**: Modifying or destroying `dev` has zero effect on `staging` or `prod`.
- **Protected Historical Baselines**:
  - `unitransit` (Docker/K8s baseline) remains untouched.
  - `unitransit-iac` (`terraform/k8s/terraform.tfstate` reference) remains untouched as a rollback baseline.
  - Production deployments will utilize remote state with distributed locking (e.g. AWS S3 + DynamoDB or GCS).

---

## 5. Promotion Model: Infrastructure vs Application Artifacts

```text
SOURCE CODE / INFRASTRUCTURE
        │
        ├── Terraform Modules (Reusable definitions)
        │     │
        │     ├── Dev variables (terraform.tfvars)
        │     ├── Staging variables (terraform.tfvars)
        │     └── Production variables (terraform.tfvars)
        │
        └── Git Commit
             │
             ▼
      CI/CD SUPPLY CHAIN (Phase 9.2)
             │
        ┌────┴────┐
        │         │
      Tests     Trivy
        │         │
        └────┬────┘
             ▼
       Immutable SHA Image
             │
             ▼
       Container Registry
             │
             ▼
       Dev → Staging → Production
```

- **Infrastructure Promotion**: The module code is identical across all environments; promotion happens by adjusting variable declarations from dev to staging to prod.
- **Application Artifact Promotion**: Code is compiled, tested (77/77 tests), vulnerability scanned via Trivy, tagged with immutable Git SHA digests, and promoted sequentially across environments without rebuilding images.

---

## 6. Current Implementation & Future Cloud Abstraction

- **Current (Phase 9.1)**: Pure Kubernetes-native manifests across all 6 modules (StatefulSet PostgreSQL, Redis Deployment, Daphne ASGI Backend, Worker Deployments, Nginx Frontend, Prometheus/Grafana) targeting local Kubernetes context (`docker-desktop`).
- **Narrowly Scoped Networking**: The `networking` module is intentionally scoped to namespace and configuration/secret primitives. In Phase 9.3, cloud networking (VPC, Subnets, NAT Gateways, Security Groups, ALB Ingress) will be introduced cleanly without breaking module interfaces.
- **Future Managed Services (Phase 9.3)**: Module interfaces (`database_host`, `service_port`, `redis_host`) are preserved such that containerized PostgreSQL StatefulSet and Redis can be swapped for managed AWS RDS / ElastiCache or GCP Cloud SQL / Memorystore with zero code changes to backend or workers.
