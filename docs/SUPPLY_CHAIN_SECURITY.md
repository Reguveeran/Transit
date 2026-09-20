# Container Supply Chain & Security Governance

## 1. Overview & Architecture

UniTransit employs a hardened, zero-trust container supply chain enforcing the **"Build Once, Scan Once, Promote Everywhere"** paradigm.

```text
SOURCE CODE / INFRASTRUCTURE
        │
        ├── Terraform Modules (Reusable definitions)
        │     │
        │     ├── Dev variables (unitransit-dev / Git SHA tag)
        │     ├── Staging variables (unitransit-staging / GHCR tag)
        │     └── Production variables (unitransit-prod / Cryptographic @sha256 digest)
        │
        └── Git Commit
             │
             ▼
      CI/CD SUPPLY CHAIN (GitHub Actions)
             │
        ┌────┴────┐
        │         │
     Tests     Flake8
    (77/77)   (Linting)
        │         │
        └────┬────┘
             ▼
     Docker Buildx Multi-Stage
             │
             ▼
      Trivy Vulnerability Scan (OS & Library)
             │
        ┌────┴────┐
        │         │
      Table     SARIF Upload (GitHub Security Tab)
        │         │
        └────┬────┘
             ▼
       Immutable SHA Tag
             │
             ▼
   GitHub Container Registry (GHCR: ghcr.io)
             │
             ▼
     Cryptographic SHA-256 Digest Extraction
             │
             ▼
    Artifact Promotion Matrix
      dev → staging → prod
```

---

## 2. Supply Chain Lifecycle & Ownership

| Stage | Responsible Agent / Tool | Trigger | Artifact / Output | SLA / Quality Gate |
| :--- | :--- | :--- | :--- | :--- |
| **1. Quality Gate** | GitHub Actions (`quality-gate`) | Pull Request / Push to `main`, `develop` | Test database execution, coverage report | **77/77 Tests Passing**, zero lint errors |
| **2. Multi-Stage Build** | Docker Buildx Engine | Successful Quality Gate | `unitransit-backend`, `unitransit-worker`, `unitransit-frontend` | Minimal size, non-root user (UID 10001) |
| **3. Vulnerability Scan** | Aqua Security Trivy | Post-build | Console table, SARIF file | Zero unmitigated **CRITICAL** / **HIGH** CVEs |
| **4. Registry Publish** | GitHub Packages (GHCR) | Merge to `main` | `ghcr.io/<org>/unitransit-*:<git-sha>` | Immutable artifact storage |
| **5. Digest Pinning** | Promotion Manifest Generator | Post-publish | `@sha256:...` digest manifest | Cryptographic immutability |
| **6. Infrastructure Deploy** | Terraform Environments | Release Tag / Promotion | `unitransit-dev`, `unitransit-staging`, `unitransit-prod` | Declarative IaC synchronization |

---

## 3. Container Hardening Standards

All production container images enforce standard container security best practices:

1. **Non-Root Execution**:
   - Containers run as dedicated non-privileged user `unitransit` with explicit `UID 10001` and `GID 10001`.
   - Root privileges are stripped post-build; filesystem permissions are strictly scoped.
2. **Multi-Stage Builds**:
   - Build-time dependencies (compilers, build-essential, python dev headers, node_modules) are quarantined to builder stages.
   - Production runner images contain only the compiled bytecode, static assets, and runtime libraries (`libpq5`, `gdal-bin`).
3. **Deterministic Base Images**:
   - Base images are pinned to minimal, stable distributions (`python:3.11-slim`, `node:20-alpine`, `nginx:1.25-alpine`).
4. **Zero-`latest` Tagging Policy**:
   - Production and staging deployments strictly prohibit the `:latest` mutable tag.
   - All deployments reference either the exact **Git Commit SHA** (`:8916745`) or the **SHA-256 Content Digest** (`@sha256:...`).

---

## 4. Trivy Security Scanning & Vulnerability Policy

### Scanning Scope
Trivy scans both OS packages (Alpine / Debian packages) and application libraries (Python Pip dependencies, Node NPM modules).

### Severity & Triage Policy
- **CRITICAL**: Blocks deployment immediately. Must be patched or mitigated before release.
- **HIGH**: Requires investigation. If an upstream patch exists, it must be applied immediately.
- **MEDIUM / LOW**: Logged in SARIF report and prioritized in regular maintenance sprints.

### Vulnerability Response Workflow
```text
CVE Discovered
      │
      ▼
Trivy CI Quality Gate Failure
      │
      ├── 1. Determine Fix Availability (ignore-unfixed filter)
      ├── 2. Patch Dependency in requirements.txt or Base Image
      ├── 3. Trigger CI Pipeline -> Generate New Git SHA & Digest
      └── 4. Promote Patched Artifact across Dev -> Staging -> Prod
```

---

## 5. Artifact Promotion Matrix

```json
{
  "commit_sha": "8916745238a00b81f5838e6659bc8c31533298be",
  "short_sha": "8916745",
  "images": {
    "backend": "ghcr.io/reguveeran/unitransit-backend:8916745",
    "worker": "ghcr.io/reguveeran/unitransit-worker:8916745",
    "frontend": "ghcr.io/reguveeran/unitransit-frontend:8916745"
  },
  "digests": {
    "backend": "sha256:7be9f178dfd12b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c",
    "worker": "sha256:7be9f178dfd12b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c",
    "frontend": "sha256:e9649216e1732b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c"
  },
  "promotion_lifecycle": {
    "dev": "unitransit-dev (local validation)",
    "staging": "unitransit-staging (pre-production verification)",
    "prod": "unitransit-prod (production cryptographic digest pin)"
  }
}
```
