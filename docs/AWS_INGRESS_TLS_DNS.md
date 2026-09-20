# UniTransit AWS Ingress, TLS, DNS & External Application Architecture Guide

## 1. Architectural Overview & Cloud Progression

```text
Phase 9.1: Modular Terraform Multi-Environment Architecture         ✅
Phase 9.2: Container Supply Chain & Immutable Digest Pinning         ✅
Phase 9.3A: AWS VPC, Subnetting, Security Groups & IAM Roles         ✅
Phase 9.3B: AWS EKS Control Plane & Managed Node Groups Architecture ✅
Phase 9.3C: AWS RDS PostgreSQL (PostGIS) & ElastiCache Redis Tier    ✅
Phase 9.3D: UniTransit Stateless Workloads Deployment on EKS         ✅
Phase 9.3E: AWS Load Balancer Controller, Ingress, TLS & DNS        ✅ (Completed Model)
```

---

## 2. External Traffic Ingestion Pipeline

```text
                             Internet
                                │
                                ▼
                       Route 53 DNS Record
                       (Alias A / AAAA)
                                │
                                ▼
                      ACM TLS Certificate
                    (TLS 1.2+ / 1.3 Strict)
                                │
                                ▼
                  AWS Application Load Balancer
                 (Public Subnets 10.0.1.0/24...)
                     Ports: 80 (HTTP) -> 443 (HTTPS)
                                │
                                ▼
                  AWS Load Balancer Controller
                (IRSA Service Account on EKS)
                                │
                                ▼
                     Kubernetes Ingress (v1)
                                │
       ┌────────────────────────┼────────────────────────┐
       │                        │                        │
       ▼                        ▼                        ▼
  Path: / (Prefix)         Path: /api (Prefix)     Path: /ws (Prefix)
  frontend-service:80      backend-service:8000    backend-service:8000
 (React Nginx Tier)        (Django REST API)       (Daphne ASGI WebSocket)
                                │                        │
                                └───────────┬────────────┘
                                            │
                                     Port 5432 / 6379
                                            │
                                ┌───────────┴───────────┐
                                ▼                       ▼
                          AWS RDS PostGIS         AWS ElastiCache
                        (Private DB Subnets)    (Private DB Subnets)
```

---

## 3. Module Breakdown (`terraform/aws/modules/`)

### A. AWS Load Balancer Controller (`alb_controller/`)
- **IRSA Integration**: Links Kubernetes Service Account `aws-load-balancer-controller` in `kube-system` to an IAM role using the EKS OpenID Connect (OIDC) provider.
- **Least-Privilege Policy**: Grants permissions strictly for ALB lifecycle, target group registration, TLS certificate discovery, and WAF/Shield association.

### B. Application Load Balancer Ingress (`ingress/`)
- **Ingress Class**: `alb`
- **Scheme**: `internet-facing` placed strictly in the 3 Public Subnets (`10.0.1.0/24`, `10.0.2.0/24`, `10.0.3.0/24`).
- **Target Type**: `ip` routing directly to EKS pod ENI IPs for low-latency routing without NodePort overhead.
- **WebSocket Timeout**: Configured `load-balancer-attributes: idle_timeout.timeout_seconds=300` to prevent premature disconnection of live bus telemetry streams.
- **Path Routing**:
  - `/` → `frontend-service` (port 80)
  - `/api` → `backend-service` (port 8000)
  - `/ws` → `backend-service` (port 8000, ASGI WebSocket upgrade)

### C. AWS Certificate Manager (`acm/`)
- **Validation**: Automatic DNS validation records with `create_before_destroy` lifecycle.
- **TLS Policy**: `ELBSecurityPolicy-TLS13-1-2-2021-06` enforcing TLS 1.2 and 1.3.
- **Conditional Provisioning**: Configurable toggle (`enable_tls = false` by default, enabled when domain is provided).

### D. Route 53 DNS (`route53/`)
- **Alias Record**: Creates route53 `A` alias pointing to the ALB canonical DNS name with health check evaluation.
- **Conditional Configuration**: Controlled by `enable_dns = false` and `hosted_zone_id`.

---

## 4. Reverse Proxy & Security Configurations

### Django Reverse Proxy Awareness
In [`backend/core/settings.py`](file:///Users/reguveeran/Downloads/Devopsproject/backend/core/settings.py), proxy headers and origins are properly configured:
- `SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")`
- `USE_X_FORWARDED_HOST = True`
- `USE_X_FORWARDED_PORT = True`
- `CORS_ALLOWED_ORIGINS` & `CSRF_TRUSTED_ORIGINS`: Loaded dynamically from environment variables.

### Frontend Endpoint Decoupling
The React frontend communicates with the environment via dynamic origin bindings:
- **Local Dev**: `http://localhost:8000` and `ws://localhost:8000`
- **AWS Cloud Production**: `https://<domain>/api` and `wss://<domain>/ws`

---

## 5. Cost & Provisioning Safety

| Component | Status in Code | Paid AWS Resources Provisioned | Incurred Cost |
| :--- | :--- | :--- | :--- |
| **VPC & Subnets** | Modeled in Terraform | **0** | **$0.00** |
| **EKS Control Plane & Nodes** | Modeled in Terraform | **0** | **$0.00** |
| **RDS PostgreSQL (PostGIS)** | Modeled in Terraform | **0** | **$0.00** |
| **ElastiCache Redis** | Modeled in Terraform | **0** | **$0.00** |
| **ALB & Ingress** | Modeled in Terraform | **0** | **$0.00** |
| **ACM & Route 53** | Modeled in Terraform | **0** | **$0.00** |
