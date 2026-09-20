# UniTransit Phase 9.3E: AWS Ingress, TLS, DNS & External Application Architecture Report

**Phase Status**: **COMPLETED & VALIDATED (Architecture & Infrastructure Modeling)**  
**Date**: September 20, 2026  
**Target Modules**: `terraform/aws/modules/{alb_controller,ingress,acm,route53}`  
**Target Environments**: `terraform/aws/environments/{dev,prod}`  

---

## 1. Executive Summary

Phase 9.3E models the external ingress, secure TLS termination, DNS alias routing, and proxy-awareness architecture for UniTransit on AWS:
1. **AWS Load Balancer Controller**: Created IAM Policy, Role, and IRSA Service Account (`aws-load-balancer-controller`) utilizing EKS OIDC federation.
2. **ALB Ingress & Path Routing**: Created Kubernetes Ingress v1 definitions routing `/` to React frontend, `/api` to Django backend, and `/ws` to Daphne ASGI WebSocket endpoint with extended 300s idle timeout.
3. **ACM & Route 53 Modules**: Modeled DNS-validated TLS certificates and Route 53 `A` alias records with conditional toggle variables (`enable_tls = false`, `enable_dns = false`).
4. **Django Proxy & Security Hardening**: Configured `SECURE_PROXY_SSL_HEADER`, `USE_X_FORWARDED_HOST`, `USE_X_FORWARDED_PORT`, `CORS_ALLOWED_ORIGINS`, and `CSRF_TRUSTED_ORIGINS` in `backend/core/settings.py`.
5. **Zero Paid AWS Provisioning / Zero Cost**: Validated with `terraform validate` across `dev` and `prod`. No paid AWS resources were provisioned.
6. **Zero Regression & Local Stability**: All 77 application tests pass (`77/77 OK`), and local namespaces (`unitransit`, `unitransit-iac`, `unitransit-dev`) remain 100% operational.

---

## 2. Ingress & Traffic Routing Architecture

```text
                     Internet
                        │
                        ▼
                 Route 53 DNS (Alias)
                        │
                        ▼
                 ACM TLS Certificate (TLS 1.2 / 1.3)
                        │
                        ▼
           AWS Application Load Balancer
                 (HTTP 80 -> HTTPS 443)
                        │
                        ▼
            AWS Load Balancer Controller (IRSA)
                        │
                        ▼
               Kubernetes Ingress (v1)
               ├── /        → frontend-service:80
               ├── /api     → backend-service:8000
               └── /ws      → backend-service:8000 (WebSocket)
```

---

## 3. Files Created & Modified

| File | Status | Description |
| :--- | :--- | :--- |
| [`terraform/aws/modules/alb_controller/variables.tf`](file:///Users/reguveeran/Downloads/Devopsproject/terraform/aws/modules/alb_controller/variables.tf) | **NEW** | ALB Controller module variables |
| [`terraform/aws/modules/alb_controller/main.tf`](file:///Users/reguveeran/Downloads/Devopsproject/terraform/aws/modules/alb_controller/main.tf) | **NEW** | IAM Policy, IRSA Role, and Service Account for ALB Controller |
| [`terraform/aws/modules/alb_controller/outputs.tf`](file:///Users/reguveeran/Downloads/Devopsproject/terraform/aws/modules/alb_controller/outputs.tf) | **NEW** | Role and Service Account outputs |
| [`terraform/aws/modules/acm/variables.tf`](file:///Users/reguveeran/Downloads/Devopsproject/terraform/aws/modules/acm/variables.tf) | **NEW** | ACM TLS module variables |
| [`terraform/aws/modules/acm/main.tf`](file:///Users/reguveeran/Downloads/Devopsproject/terraform/aws/modules/acm/main.tf) | **NEW** | Conditional ACM certificate resource with DNS validation |
| [`terraform/aws/modules/acm/outputs.tf`](file:///Users/reguveeran/Downloads/Devopsproject/terraform/aws/modules/acm/outputs.tf) | **NEW** | Certificate ARN output |
| [`terraform/aws/modules/route53/variables.tf`](file:///Users/reguveeran/Downloads/Devopsproject/terraform/aws/modules/route53/variables.tf) | **NEW** | Route 53 DNS module variables |
| [`terraform/aws/modules/route53/main.tf`](file:///Users/reguveeran/Downloads/Devopsproject/terraform/aws/modules/route53/main.tf) | **NEW** | Conditional Route 53 Alias record to ALB |
| [`terraform/aws/modules/route53/outputs.tf`](file:///Users/reguveeran/Downloads/Devopsproject/terraform/aws/modules/route53/outputs.tf) | **NEW** | FQDN record output |
| [`terraform/aws/modules/ingress/variables.tf`](file:///Users/reguveeran/Downloads/Devopsproject/terraform/aws/modules/ingress/variables.tf) | **NEW** | Ingress module parameters (subnets, security groups, ports) |
| [`terraform/aws/modules/ingress/main.tf`](file:///Users/reguveeran/Downloads/Devopsproject/terraform/aws/modules/ingress/main.tf) | **NEW** | Kubernetes Ingress v1 with ALB annotations & path routing |
| [`terraform/aws/modules/ingress/outputs.tf`](file:///Users/reguveeran/Downloads/Devopsproject/terraform/aws/modules/ingress/outputs.tf) | **NEW** | Ingress name and namespace outputs |
| [`backend/core/settings.py`](file:///Users/reguveeran/Downloads/Devopsproject/backend/core/settings.py) | **MODIFIED** | Added proxy SSL header and dynamic CORS/CSRF configurations |
| [`terraform/aws/environments/dev/variables.tf`](file:///Users/reguveeran/Downloads/Devopsproject/terraform/aws/environments/dev/variables.tf) | **MODIFIED** | Added Ingress, TLS, and DNS toggles |
| [`terraform/aws/environments/dev/main.tf`](file:///Users/reguveeran/Downloads/Devopsproject/terraform/aws/environments/dev/main.tf) | **MODIFIED** | Wired `alb_controller`, `acm`, `ingress`, and `route53` modules |
| [`terraform/aws/environments/dev/outputs.tf`](file:///Users/reguveeran/Downloads/Devopsproject/terraform/aws/environments/dev/outputs.tf) | **MODIFIED** | Added `ingress` metadata output |
| [`terraform/aws/environments/prod/variables.tf`](file:///Users/reguveeran/Downloads/Devopsproject/terraform/aws/environments/prod/variables.tf) | **MODIFIED** | Added Ingress, TLS, and DNS production toggles |
| [`terraform/aws/environments/prod/main.tf`](file:///Users/reguveeran/Downloads/Devopsproject/terraform/aws/environments/prod/main.tf) | **MODIFIED** | Wired `alb_controller`, `acm`, `ingress`, and `route53` modules |
| [`terraform/aws/environments/prod/outputs.tf`](file:///Users/reguveeran/Downloads/Devopsproject/terraform/aws/environments/prod/outputs.tf) | **MODIFIED** | Added `ingress` production metadata output |
| [`docs/AWS_INGRESS_TLS_DNS.md`](file:///Users/reguveeran/Downloads/Devopsproject/docs/AWS_INGRESS_TLS_DNS.md) | **NEW** | Complete architectural documentation for Ingress, TLS, and DNS |

---

## 4. Validation & Verification Results

1. **Terraform Formatting**:
   - Command: `terraform fmt -check -recursive terraform/aws`
   - Result: **PASS** (Zero formatting issues)
2. **Terraform Validation**:
   - Dev Environment: `terraform validate` — **Success! The configuration is valid.**
   - Prod Environment: `terraform validate` — **Success! The configuration is valid.**
3. **Terraform Plan Status**:
   - Requires live AWS credentials. In absence of active AWS credentials, plan stops with `No valid credential sources found`, guaranteeing that **zero paid AWS resources were provisioned**.
4. **Application Regression Tests**:
   - Command: `PYTHONPATH=backend:. .venv/bin/python backend/manage.py test tests`
   - Result: **Ran 77 tests in 30.702s. OK (77/77 PASS)**.
5. **Protected Local Kubernetes Status**:
   - `unitransit-dev`: **8/8 Pods Running**
   - `unitransit-iac`: **8/8 Pods Running**
   - `unitransit`: **6/6 Pods Running**
6. **Paid AWS Resources Created**: **0 (Zero)**

---

## 5. Live AWS Deployment Distinction

| Scope | Status | Notes |
| :--- | :--- | :--- |
| **Terraform & Kubernetes Ingress Model** | **Fully Modeled & Validated** | All modules ready for deployment |
| **Paid AWS Resources Provisioned** | **None (0 Resources Created)** | Strict zero-cost policy maintained |
| **Live External DNS / TLS / ALB** | **Not Deployed** | Pending explicit AWS deployment decision |

---

## 6. Full Progression Status

```text
9.1  Modular Terraform (Completed)
       ↓
9.2  Secure Container Supply Chain (Completed)
       ↓
9.3A AWS VPC + Security + IAM (Completed)
       ↓
9.3B EKS Architecture + Node Groups (Completed)
       ↓
9.3C Managed Data Tier (Completed)
       ↓
9.3D Deploy UniTransit to EKS (Completed)
       ↓
9.3E Ingress + TLS + DNS (Completed)
       ↓
Phase 10: Live AWS Cloud Deployment (When Ready)
```
