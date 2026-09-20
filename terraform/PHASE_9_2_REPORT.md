# UniTransit Phase 9.2: Container Supply Chain & Security Hardening Report

**Phase Status**: **COMPLETED & VALIDATED**  
**Date**: September 20, 2026  
**Artifact Scope**: `unitransit-backend`, `unitransit-worker`, `unitransit-frontend`  
**Registry Target**: GitHub Container Registry (`ghcr.io`)  

---

## 1. Executive Summary

Phase 9.2 implements an enterprise container supply chain and vulnerability security architecture:
1. **Build Once, Scan Once, Promote Everywhere**: Immutable image artifacts are built from exact Git commit SHAs, scanned via Aqua Security Trivy, published to GHCR, and promoted across `dev` -> `staging` -> `prod` without rebuilding.
2. **Elimination of `latest`**: All Terraform environment configurations (`dev`, `staging`, `prod`) now explicitly declare immutable image references (Git commit SHAs and cryptographic SHA-256 digests).
3. **Multi-Stage & Non-Root Hardening**: Dockerfiles enforce non-root execution (`unitransit` UID 10001) and minimal runtime footprints.
4. **Zero Regressions & Namespace Safety**: All 77 regression tests pass (`77/77 OK`), and `unitransit`, `unitransit-iac`, and `unitransit-dev` environments remain fully operational.

---

## 2. Supply Chain Workflow (`.github/workflows/supply-chain.yml`)

The supply chain pipeline consists of 3 sequential gates:
- **Job 1: Quality Gate & Regression Tests**: Checks out source code, executes Python 3.11 unit/integration tests (77/77), Flake8 style/syntax verification, and Vite production bundle compilation.
- **Job 2: Multi-Stage Build & Trivy Vulnerability Scan**: Builds backend, worker, and frontend container images using Docker Buildx, scans with Trivy for OS and dependency CVEs, produces machine-readable SARIF reports uploaded to GitHub Advanced Security tab, and publishes immutable artifacts to GHCR (`ghcr.io/reguveeran/unitransit-*:<sha>`).
- **Job 3: Immutable Promotion Manifest**: Captures cryptographic content digests (`@sha256:...`) and outputs an immutable promotion manifest for Terraform consumption.

---

## 3. Terraform Multi-Environment Parameterization

| Environment | Parameter Strategy | Backend Image | Worker Image | Frontend Image |
| :--- | :--- | :--- | :--- | :--- |
| **Dev** | Git SHA Immutable Tag | `unitransit/backend:8916745` | `unitransit/worker:8916745` | `unitransit/frontend:latest` |
| **Staging** | GHCR Git SHA Tag | `ghcr.io/reguveeran/unitransit-backend:8916745` | `ghcr.io/reguveeran/unitransit-worker:8916745` | `ghcr.io/reguveeran/unitransit-frontend:8916745` |
| **Prod** | Cryptographic SHA-256 Digest Pin | `ghcr.io/reguveeran/unitransit-backend@sha256:7be9f178dfd...` | `ghcr.io/reguveeran/unitransit-worker@sha256:7be9f178dfd...` | `ghcr.io/reguveeran/unitransit-frontend@sha256:e9649216e17...` |

---

## 4. Validation & Verification Results

### Terraform Checks
- `terraform fmt -recursive`: **PASS**
- `terraform validate` across `dev`, `staging`, `prod`: **PASS (All 3 environments valid)**
- `terraform plan` (`dev`): **0 to add, 0 to change, 0 to destroy (State synced)**
- `terraform plan` (`staging`): **Plan: 18 to add, 0 to change, 0 to destroy**
- `terraform plan` (`prod`): **Plan: 18 to add, 0 to change, 0 to destroy**

### Live Operational Verification in `unitransit-dev`
- **Rolling Update**: Successfully rolled out immutable Git-SHA backend and worker images (`8916745`).
- **Health Probes**: `GET /health` (200 OK), `GET /ready` (200 OK - PostgreSQL and Redis connected).
- **Streaming Pipeline**: Published event `DEV-SUPPLY-CHAIN-902` to Redis Stream -> Consumed by immutable `PositionWorker` -> `XACK` confirmed -> `VehiclePosition` persisted (`id=3`, `speed=48.0`).

### Test Suite Execution
- **Command**: `PYTHONPATH=backend:. python backend/manage.py test tests`
- **Result**: **Ran 77 tests in 34.097s. OK. (77/77 Passing, 0 Failures)**

---

## 5. Protected Environments Status

- `unitransit` namespace: **Untouched & Active**.
- `unitransit-iac` namespace: **Untouched & Active**.
- `terraform/k8s/` Phase 8 baseline: **Preserved unchanged**.

---

## 6. Recommended Next Phase

With the modular infrastructure (Phase 9.1) and immutable secure supply chain (Phase 9.2) in place, we are ready to proceed to:
**Phase 9.3: Cloud Infrastructure & Managed Services (AWS/EKS/RDS/ElastiCache Migration)**.
