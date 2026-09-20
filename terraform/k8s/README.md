# UniTransit - Kubernetes Infrastructure as Code (Terraform)

This directory contains the declarative Infrastructure as Code (IaC) configuration for UniTransit using the official HashiCorp `kubernetes` provider.

## Architecture

```text
Terraform (terraform/k8s/)
   │
   ├── Namespace (unitransit-iac)
   ├── ConfigMaps & Secrets (unitransit-config, unitransit-secrets)
   ├── Redis (Stream Broker Deployment & Service)
   ├── PostgreSQL / PostGIS (StatefulSet & Service with 5Gi PVC)
   ├── Backend (Django + Channels + DRF API Deployment & Service)
   ├── Position & Alert Workers (Deployments)
   ├── Frontend (Vite + Nginx Deployment & Service)
   └── Monitoring (Prometheus & Grafana Deployments & Services)
        ↓
   Kubernetes Cluster (docker-desktop context)
```

## Why Terraform?

1. **Declarative State**: Infrastructure is represented as immutable code rather than manual `kubectl apply` commands.
2. **State Management**: `terraform.tfstate` maps real-world cluster resources to configuration.
3. **Drift Detection**: `terraform plan` detects when someone manually alters cluster properties (e.g. replica count, env vars).
4. **Reproducibility**: The entire environment can be destroyed and recreated cleanly with zero configuration drift.

## Safety & Namespace Isolation

This Terraform stack targets an isolated namespace:
```hcl
variable "namespace" {
  default = "unitransit-iac"
}
```
The existing development namespace (`unitransit`) remains **completely untouched**.

## Usage

### 1. Initialize Provider
```bash
terraform init
```

### 2. Format & Validate
```bash
terraform fmt -recursive
terraform validate
```

### 3. Review Execution Plan
```bash
terraform plan
```

### 4. Apply Infrastructure
```bash
terraform apply -auto-approve
```

### 5. Inspect Created Environment
```bash
kubectl get all -n unitransit-iac
kubectl get pvc -n unitransit-iac
```

### 6. Drift Detection Experiment
```bash
# Manually scale replicas outside Terraform
kubectl scale deployment worker-position --replicas=3 -n unitransit-iac

# Run plan to detect configuration drift
terraform plan

# Reapply to restore declared configuration
terraform apply -auto-approve
```

### 7. Destroy & Recreate Experiment
```bash
# Destroy isolated environment
terraform destroy -auto-approve

# Verify cleanup
kubectl get all -n unitransit-iac

# Recreate from pure code
terraform apply -auto-approve
```
