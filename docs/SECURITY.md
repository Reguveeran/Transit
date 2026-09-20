# UniTransit Security Architecture & Posture

UniTransit adheres to enterprise defense-in-depth principles across the entire application, container supply chain, and infrastructure layers.

---

## 1. Secrets & Credential Management
- **Zero Secrets in Code**: No passwords, tokens, API keys, or private certificates are committed to the repository.
- **Runtime Decoupling**: Database passwords, Django secret keys, and broker credentials are parameterized as sensitive Terraform variables and injected into Kubernetes Secrets at runtime.
- **Environment Example Files**: All `.tfvars.example` files use explicit `CHANGE_ME` placeholders.
- **Git Protection**: `.gitignore` strictly excludes `.env`, `*.tfvars`, `*.tfstate`, and certificate files (`*.pem`, `*.key`).

---

## 2. Container Supply Chain Security (`.github/workflows/supply-chain.yml`)
- **Multi-Stage Builds**: Final runtime container images exclude compilation tools, package managers, and source build dependencies.
- **Non-Root Execution**: Backend and worker containers execute as unprivileged user `unitransit` (UID `10001`).
- **Static Vulnerability Scanning**: Aqua Security Trivy scans all container images during CI prior to registry publishing, uploading SARIF reports to GitHub Security Advisory.
- **Immutable Digest Promotion**: Production manifests pin container images via cryptographic SHA-256 digests (`image@sha256:...`) eliminating supply chain mutation risks associated with mutable tags (`latest`).

---

## 3. Kubernetes & Cluster Hardening
- **Probes & Isolation**: `startupProbe`, `livenessProbe`, and `readinessProbe` prevent traffic routing to unready containers and isolate crashing pods.
- **Resource Boundary Enforcement**: Explicit CPU and Memory requests/limits prevent noisy neighbor resource starvation and OOM denial-of-service.
- **Controlled Migration Job**: Database migrations run as an isolated Kubernetes Job (`unitransit-db-migrate`) with PostGIS verification, preventing concurrent migration lock contention.

---

## 4. AWS Cloud Security Architecture (Declarative)
- **IAM Least Privilege & IRSA**: AWS Load Balancer Controller uses IAM Roles for Service Accounts (IRSA) tied to the EKS OIDC provider with strictly scoped IAM policies.
- **Micro-Segmented Security Groups**:
  - `rds_sg`: Ingress strictly allowed on port 5432 from `eks_nodes_sg`.
  - `elasticache_sg`: Ingress strictly allowed on port 6379 from `eks_nodes_sg`.
  - Zero direct internet access to database or caching tiers.
- **Network Isolation**: All persistent databases and Redis replication clusters reside in dedicated Private Database Subnets.
- **TLS Everywhere**: RDS enforces SSL (`rds.force_ssl = 1`), ElastiCache enforces in-transit encryption, and ALB Ingress enforces TLS 1.2+ (`ELBSecurityPolicy-TLS13-1-2-2021-06`).
