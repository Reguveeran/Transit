# Terraform Infrastructure as Code

Modular Terraform configurations for provisioning cloud-native infrastructure for UniTransit.

## Structure
- `modules/`: Reusable Terraform modules (`vpc`, `eks`/`gke`, `rds_postgis`, `elasticache_redis`, `monitoring`).
- `environments/dev/`: Developer cloud deployment environment.
- `environments/prod/`: Production high-availability deployment environment.
