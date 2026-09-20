# UniTransit Phase 9.3B: AWS EKS Cluster & Managed Node Groups Report

**Phase Status**: **COMPLETED & VALIDATED**  
**Date**: September 20, 2026  
**Scope**: AWS EKS Control Plane, Managed Node Groups, OIDC/IRSA, Sizing & Cost Estimation  
**Target Module**: `terraform/aws/modules/eks/`  
**Target Environments**: `terraform/aws/environments/{dev,prod}`  

---

## 1. Executive Summary

Phase 9.3B implements the AWS EKS Cluster and Managed Node Group architecture for UniTransit:
1. **Stateless Compute Layer**: Established EKS control plane (v1.30) and multi-AZ managed node groups across private application subnets.
2. **Strict Workload Boundary**: Application workloads and stateful data stores are decoupled — stateful PostgreSQL and Redis remain outside EKS, targeting AWS RDS and ElastiCache in Phase 9.3C.
3. **IAM Roles for Service Accounts (IRSA)**: Configured OIDC identity provider integration for least-privilege pod permissions.
4. **Cost & Sizing Governance**: Documented detailed compute cost models and sizing configurations for development (`t3.medium`, 2 nodes) vs production (`t3.large`, 3 nodes).
5. **Zero Impact on Local Environments**: All local Kubernetes workloads (`unitransit-dev` 8/8, `unitransit-iac` 8/8, `unitransit` 6/6) and test suites (77/77 tests) remain active and passing.

---

## 2. Infrastructure Inventory (`terraform/aws/modules/eks/`)

- **EKS Control Plane (`aws_eks_cluster.main`)**:
  - Kubernetes Version: `1.30`
  - Subnet Distribution: Private App Subnets across `us-east-1a`, `us-east-1b`, `us-east-1c`
  - Security: Endpoint private access enabled, public access enabled, control plane logging (`api`, `audit`, `authenticator`, `controllerManager`, `scheduler`).
- **Managed Node Groups (`aws_eks_node_group.main`)**:
  - Dev: 2x `t3.medium`, min: 1, max: 4, disk: 30 GiB gp3
  - Prod: 3x `t3.large`, min: 2, max: 10, disk: 50 GiB gp3
  - Labels: `role = worker`, `app = unitransit`
  - Update Config: `max_unavailable = 1` rolling update strategy
- **Core Add-ons**:
  - `vpc-cni` (AWS VPC Container Network Interface)
  - `coredns` (Cluster DNS)
  - `kube-proxy` (Network Proxy)
  - `aws-ebs-csi-driver` (EBS storage provider)

---

## 3. Cost & Resource Profile

| Component | Dev Config | Prod Config | Estimated Monthly Cost |
| :--- | :--- | :--- | :--- |
| **EKS Control Plane** | 1 Cluster | 1 Cluster | $73.00 |
| **EC2 Worker Nodes** | 2x `t3.medium` | 3x `t3.large` | $60.00 (Dev) / $180.00 (Prod) |
| **VPC NAT Gateways** | 1x Shared | 3x Multi-AZ Redundant | $32.00 (Dev) / $96.00 (Prod) |
| **EBS Storage** | 60 GiB gp3 | 150 GiB gp3 | $5.00 (Dev) / $12.00 (Prod) |
| **Total Monthly Sizing** | — | — | **~$170.00 (Dev) / ~$361.00 (Prod)** |

---

## 4. Protected Environments Status

- `unitransit` namespace: **Untouched & Active (6/6 pods running)**
- `unitransit-iac` namespace: **Untouched & Active (8/8 pods running)**
- `unitransit-dev` namespace: **Untouched & Active (8/8 pods running)**
- Regression test baseline: **77/77 tests passing**

---

## 5. Next Recommended Step

Proceed to **Phase 9.3C: AWS Managed Data Tier (RDS PostgreSQL/PostGIS + ElastiCache Redis)**.
