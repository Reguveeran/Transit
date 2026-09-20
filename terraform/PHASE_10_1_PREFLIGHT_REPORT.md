# UniTransit Phase 10.1: AWS Identity & Zero-Cost Preflight Report

**Report Date**: September 20, 2026  
**Phase Status**: **BLOCKED_CREDENTIALS** (Safe expected preflight state)  
**Cost Incurred**: **$0.00 (Zero AWS resources provisioned)**  

---

## 1. Executive Summary

Phase 10.1 performs a read-only, zero-cost preflight audit prior to commencing Phase 10 live cloud infrastructure deployment. 

The audit evaluated:
1. **AWS CLI & Caller Identity**: Checked local environment for AWS credentials and authentication sessions.
2. **Terraform Integrity**: Confirmed formatting and syntax validation across `dev` and `prod` configurations.
3. **Security & Credential Audit**: Verified zero exposed access keys, passwords, or private keys across the codebase and `.tfvars`.
4. **Git State Safety**: Verified that `.gitignore` correctly protects `.tfstate` and `.terraform` directories.
5. **Local Health & Test Baseline**: Confirmed all 3 local Kubernetes namespaces are active and **77/77 tests passed**.

---

## 2. Preflight Findings & Audit Results

### A. AWS CLI & Authentication Identity
- **AWS CLI Installation**: `aws --version` returned `command not found` (Not installed in local system PATH).
- **STS Caller Identity**: `aws sts get-caller-identity` could not be executed; no active session or credentials found.
- **Configured Region**: `us-east-1` (Declared across Terraform variables).
- **Authentication Status**: **BLOCKED_CREDENTIALS** (AWS CLI installation and SSO/STS authentication session required before Phase 10.2).

### B. Terraform State & Configuration Safety
- **Terraform Formatting**: `terraform fmt -check -recursive terraform/aws` — **PASS**.
- **Dev Configuration**: `terraform validate` (`terraform/aws/environments/dev`) — **Success! The configuration is valid.**
- **Prod Configuration**: `terraform validate` (`terraform/aws/environments/prod`) — **Success! The configuration is valid.**
- **Tfvars Safety**: Inspected `terraform/aws/environments/dev/terraform.tfvars` and `terraform/aws/environments/prod/terraform.tfvars`. Only non-sensitive architectural variables (`aws_region`, `environment`, `vpc_cidr`, `cluster_name`) are declared. **Zero secrets in tfvars**.

### C. Credential Safety Audit
- Pattern Scan (`AKIA...`, `BEGIN RSA/PRIVATE KEY`): **Zero exposed credentials detected**.
- Sensitive values (`POSTGRES_PASSWORD`, `DJANGO_SECRET_KEY`) are properly parameterized as sensitive Terraform variables.

### D. Git State Safety
- `.gitignore` verification: Covers `.terraform/*`, `*.tfstate`, `*.tfstate.*`, `*.pem`, `*.key`, `*.crt`.
- State files: Not tracked in Git repository.

### E. Application Regression & Local Kubernetes Health
- **Test Suite**: `PYTHONPATH=backend:. .venv/bin/python backend/manage.py test tests`
- **Result**: **Ran 77 tests in 30.089s. OK (77/77 PASS)**.
- **Local Kubernetes Namespaces**:
  - `unitransit-dev`: **8/8 Pods Running**
  - `unitransit-iac`: **8/8 Pods Running**
  - `unitransit`: **6/6 Pods Running**

---

## 3. Expected Cost-Bearing Services (For Future Deployment Phases)

When Phase 10 live deployment is authorized, charges will begin on the following components:

| Component | Target Micro-Phase | Sizing (Dev) | Sizing (Prod) | Projected Monthly Profile |
| :--- | :--- | :--- | :--- | :--- |
| **NAT Gateways** | Phase 10.2 (VPC) | 1x Shared NAT | 3x Multi-AZ NAT | ~$32 (Dev) / ~$96 (Prod) |
| **EKS Control Plane** | Phase 10.4 (EKS) | 1x Cluster (v1.30) | 1x Cluster (v1.30) | ~$73 (Dev) / ~$73 (Prod) |
| **EC2 Worker Nodes** | Phase 10.4 (EKS) | 2x `t3.medium` | 3x `t3.large` | ~$60 (Dev) / ~$180 (Prod) |
| **RDS PostgreSQL (PostGIS)**| Phase 10.5 (RDS) | 1x `db.t4g.medium` (20 GiB)| 1x `db.r6g.large` Multi-AZ (100 GiB) | ~$65 (Dev) / ~$340 (Prod) |
| **ElastiCache Redis** | Phase 10.6 (Cache) | 1x `cache.t4g.small` | 3x `cache.r6g.large` Multi-AZ | ~$25 (Dev) / ~$480 (Prod) |
| **Application Load Balancer**| Phase 10.9 (Ingress) | 1x ALB | 1x ALB | ~$20 (Dev) / ~$20 (Prod) |
| **Total Projected Profile** | — | — | — | **~$275 / mo (Dev) / ~$1,189 / mo (Prod)** |

---

## 4. Final Classification & Next Action

### **Preflight Status**: `BLOCKED_CREDENTIALS`

```text
AWS identity & CLI      ❌  AWS CLI / STS session required
Region compatibility    ✅  us-east-1 validated
Terraform validation    ✅  dev + prod passing
Credential audit        ✅  Zero secrets exposed
Git safety              ✅  .gitignore & state files protected
Local Kubernetes        ✅  22/22 pods running across all 3 namespaces
Application test suite  ✅  77/77 tests passing
Paid AWS resources      0 created ($0.00 spent)
```

### Recommendation Before Phase 10.2:
1. Install AWS CLI: `brew install awscli` (or official AWS package).
2. Configure short-lived credentials via AWS IAM Identity Center / AWS SSO:
   ```bash
   aws configure sso
   # or
   aws sso login --profile <profile-name>
   ```
3. Once authenticated (`aws sts get-caller-identity` returns valid Account ID and Role ARN), proceed to **Phase 10.2: VPC & Networking Provisioning (Plan & Review Gate)**.
