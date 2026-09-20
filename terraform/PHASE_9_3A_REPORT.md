# UniTransit Phase 9.3A: AWS Cloud Foundation Report

**Phase Status**: **COMPLETED & VALIDATED**  
**Date**: September 20, 2026  
**Scope**: AWS VPC, Multi-AZ Subnets, Route Tables, Security Groups, IAM Roles  
**Target Environments**: `terraform/aws/environments/{dev,prod}`  

---

## 1. Executive Summary

Phase 9.3A establishes the core AWS Cloud Infrastructure Foundation for UniTransit without impacting the validated local Kubernetes environments.
- **VPC & Subnet Tiering**: Provisions a 3-tier Multi-AZ network topology (Public, Private App for EKS, Private DB for RDS/Redis) across 3 availability zones (`us-east-1a`, `us-east-1b`, `us-east-1c`).
- **Security Micro-Segmentation**: Implements least-privilege security groups separating public ALBs, EKS control plane, worker nodes, and isolated database/cache tiers.
- **EKS IAM Governance**: Configures IAM roles and policy attachments for the EKS control plane and managed node groups.
- **Cost & HA Optimization**:
  - `dev`: Single NAT Gateway for cost-efficiency with full Multi-AZ subnet distribution.
  - `prod`: Redundant Multi-AZ NAT Gateways for zero single-point-of-failure high availability.

---

## 2. Directory & Module Structure

```text
terraform/aws/
├── modules/
│   ├── vpc/
│   │   ├── main.tf                 # VPC, IGW, Subnets, EIPs, NAT Gateways, Route Tables, DB Subnet Group
│   │   ├── variables.tf            # Parameterized CIDRs, AZs, cluster name, single_nat_gateway flag
│   │   └── outputs.tf              # VPC ID, Subnet ID lists, DB subnet group, NAT public IPs
│   │
│   ├── security_groups/
│   │   ├── main.tf                 # ALB SG, EKS Cluster SG, EKS Node SG, RDS SG, ElastiCache SG
│   │   ├── variables.tf            # VPC ID, environment, cluster name
│   │   └── outputs.tf              # Security Group IDs
│   │
│   └── iam/
│       ├── main.tf                 # EKS Cluster role, EKS Node Group role, Managed policy attachments
│       ├── variables.tf            # Environment, cluster name
│       └── outputs.tf              # Role ARNs and names
│
└── environments/
    ├── dev/
    │   ├── main.tf                 # AWS Provider, VPC (Single NAT), Security Groups, IAM modules
    │   ├── variables.tf
    │   ├── terraform.tfvars        # us-east-1, vpc_cidr = 10.0.0.0/16
    │   ├── outputs.tf
    │   └── versions.tf             # AWS Provider ~> 5.0
    │
    └── prod/
        ├── main.tf                 # AWS Provider, VPC (Multi-AZ Redundant NAT), Security Groups, IAM modules
        ├── variables.tf
        ├── terraform.tfvars        # us-east-1, vpc_cidr = 10.100.0.0/16
        ├── outputs.tf
        └── versions.tf             # AWS Provider ~> 5.0
```

---

## 3. Subnet & Security Architecture Matrix

| Subnet / Tier | Multi-AZ Distribution | Routing / Egress | Security Ingress Boundary |
| :--- | :--- | :--- | :--- |
| **Public Subnets** | `us-east-1a, 1b, 1c` | Direct to IGW (`0.0.0.0/0`) | Ports 80 & 443 from Internet (`0.0.0.0/0`) |
| **Private App Subnets** | `us-east-1a, 1b, 1c` | Outbound via NAT Gateway | Traffic from ALB SG + Control Plane (1025-65535) + Node-to-node |
| **Private DB Subnets** | `us-east-1a, 1b, 1c` | Isolated (No IGW or NAT route) | Port 5432 (RDS) and Port 6379 (Redis) strictly from Node SG |

---

## 4. Protected Environments Confirmation

- `unitransit` namespace: **Untouched & Active (6/6 workloads running)**
- `unitransit-iac` namespace: **Untouched & Active (8/8 workloads running)**
- `unitransit-dev` namespace: **Untouched & Active (8/8 workloads running)**
- Application regression test baseline: **77/77 tests passing**

---

## 5. Next Steps

With Phase 9.3A (AWS Cloud Foundation) complete, the infrastructure is prepared for:
**Phase 9.3B: AWS EKS Cluster & Managed Node Groups Deployment**.
