# UniTransit: The DevOps & SRE Engineering Journey

This document chronicles the progressive transformation of UniTransit from a real-time transit telemetry application into an enterprise-grade, cloud-native, fault-tolerant platform.

---

## Evolution Timeline

```text
Phase 1: Real-Time Event Ingestion (ASGI, Redis Streams, Spatial Processing)
   ↓
Phase 2: Observability & Telemetry (Prometheus, Custom Metrics, Grafana)
   ↓
Phase 3: Worker Reliability & Horizontal Scaling (Consumer Groups, Poison-Pill Dead-Lettering)
   ↓
Phase 4: Chaos Engineering & Failure Recovery (PEL Reclaim, Auto-Recovery)
   ↓
Phase 5: Kubernetes Container Orchestration (Self-Healing, Probes, Resource Limits)
   ↓
Phase 6: CI/CD Automation & Quality Gates (GitHub Actions, Regression Gates)
   ↓
Phase 7: Canary Deployments & SLO Error Budgets (Automated Rollback Engine)
   ↓
Phase 8: Infrastructure as Code Baseline (Terraform Local Kubernetes)
   ↓
Phase 9.1: Modular Multi-Environment Terraform (Dev, Staging, Prod Roots)
   ↓
Phase 9.2: Container Supply Chain & Vulnerability Security (Trivy, GHCR, SHA-256 Digest Pins)
   ↓
Phase 9.3A–E: Declarative AWS Cloud Architecture (VPC, EKS, RDS PostGIS, ElastiCache, ALB Ingress)
```

---

## Detailed Phase Breakdown & Learning Outcomes

### Phase 1: Real-Time Telemetry & Spatial Ingestion
- **Architecture**: Async Python/Django backend using Daphne ASGI server, Redis Streams (`transport.events`), and PostgreSQL/PostGIS.
- **Key Insight**: Decoupling real-time ingest from database writes via stream buffers prevents database connection exhaustion during peak traffic bursts (10,000+ events/sec).

### Phase 2: Telemetry & Observability Pipeline
- **Architecture**: Prometheus metric instrumentation across ingest rate (`unitransit_events_published_total`), consumer throughput (`unitransit_events_processed_total`), processing latency histograms, and consumer lag gauges.
- **Key Insight**: Real-time consumer lag (`unitransit_stream_consumer_lag`) is the ultimate leading indicator of downstream pipeline health.

### Phase 3: Consumer Group Reliability & Stream Worker Pools
- **Architecture**: `PositionWorker` pool utilizing Redis consumer groups (`unitransit_workers`).
- **Resilience Mechanisms**: Explicit ACK semantics (`XACK`), pending entry list (PEL) inspection, automated claim (`XAUTOCLAIM`), and poison-pill message isolation.

### Phase 4: Chaos Engineering & Fault Tolerance
- **Simulations**: Worker crash injection, intermittent Redis connectivity drops, corrupted telemetry payloads, and high-load stress testing.
- **Learning**: Implementing backoff retry loops and poison-pill quarantine ensures zero pipeline stalls during upstream data corruption.

### Phase 5: Kubernetes Orchestration & Self-Healing
- **Architecture**: Declarative manifests for Daphne backend, streaming workers, Redis, PostgreSQL, Prometheus, and Grafana.
- **Resilience**: Configured `startupProbe`, `livenessProbe`, and `readinessProbe` with resource requests/limits preventing memory starvation.

### Phase 6: Automated CI/CD & Test Automation
- **Pipeline**: GitHub Actions executing 77 unit, integration, and spatial regression tests, Flake8 linting, and Vite frontend asset compilation on every push.

### Phase 7: Canary Deployments & SLO-Based Rollbacks
- **Architecture**: Implemented automated canary deployment engine with fine-grained traffic shifting (10% -> 50% -> 100%) driven by Prometheus SLO evaluations (p95 latency < 200ms, error rate < 1.0%).
- **Automated Rollback**: Triggers instant rollback if error budget burn rate exceeds safe thresholds.

### Phase 8: Declarative Infrastructure as Code (Terraform)
- **Baseline**: Provisioned local Kubernetes infrastructure (`unitransit-iac`) via Terraform, verifying drift detection and full recreate idempotency.

### Phase 9.1: Modular Terraform Refactoring
- **Architecture**: Decomposed monolithic Terraform into 6 reusable modules (`networking`, `database`, `cache`, `compute`, `frontend`, `monitoring`) supporting `dev`, `staging`, and `prod` environment roots.

### Phase 9.2: Container Supply Chain & Security Hardening
- **Security**: Built multi-stage Dockerfiles, non-root user execution (UID 10001), Aqua Security Trivy vulnerability scanning, SARIF export, GHCR publishing, and immutable cryptographic SHA-256 digest pinning.

### Phase 9.3A–E: Enterprise AWS Cloud Architecture
- **9.3A**: Multi-AZ VPC with Public, Private App, and Private DB subnets, Security Groups, and IAM roles.
- **9.3B**: EKS Cluster (v1.30) with Managed Node Groups and OIDC/IRSA federation.
- **9.3C**: AWS RDS PostgreSQL with PostGIS and AWS ElastiCache Redis replication groups.
- **9.3D**: EKS Stateless Workload deployment and controlled migration job (`unitransit-db-migrate`).
- **9.3E**: AWS Load Balancer Controller, ALB Ingress, ACM TLS, and Route 53 DNS routing.

---

## Architectural Distinctions Summary

> "I separate infrastructure promotion from artifact promotion. Terraform defines the environments, while CI builds and scans the container once, publishes an immutable artifact, extracts its digest, and promotes that exact artifact across Dev, Staging, and Prod without rebuilding."
