# Terraform Cloud Infrastructure Guide

Provisioning AWS cloud infrastructure for the UniTransit platform across `dev` and `prod` environments.

## Architecture
- **VPC Module**: Isolated multi-AZ network with public and private subnets, internet gateways, and route tables.
- **EKS Module**: Managed Kubernetes cluster with managed auto-scaling node groups.
- **RDS Module**: High-availability PostgreSQL database with PostGIS extensions.
- **ElastiCache Redis Module**: Redis replication group for real-time telemetry streaming and Channels pub/sub.

---

## Deployment Instructions

### 1. Prerequisites
- Terraform CLI >= 1.5.0
- AWS CLI configured with appropriate IAM credentials (`aws configure`)

### 2. Provision Development Environment
```bash
cd terraform/environments/dev

# Copy example variables
cp terraform.tfvars.example terraform.tfvars

# Initialize providers and modules
terraform init

# Review execution plan
terraform plan

# Apply infrastructure changes
terraform apply -auto-approve
```

### 3. Connect to EKS Cluster
```bash
aws eks update-kubeconfig --region us-east-1 --name dev-unitransit-eks

# Verify nodes
kubectl get nodes
```

### 4. Teardown Infrastructure
```bash
terraform destroy -auto-approve
```
