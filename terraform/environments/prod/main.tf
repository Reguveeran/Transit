provider "kubernetes" {
  config_path    = var.kubeconfig_path
  config_context = var.kubeconfig_context
}

# ==============================================================================
# 1. Networking Module (Namespace & Config/Secret primitives)
# ==============================================================================
# In Phase 9.3 (Cloud Migration), this will be supplemented by or coupled with:
# - Cloud VPC, Private/Public Subnets, NAT Gateways, Security Groups
# - AWS ALB / Ingress Controller & Route53 / Cloudflare DNS
# ==============================================================================
module "networking" {
  source = "../../modules/networking"

  namespace         = var.namespace
  environment       = var.environment
  postgres_db       = var.postgres_db
  postgres_user     = var.postgres_user
  postgres_password = var.postgres_password
  secret_key        = var.secret_key
}

# ==============================================================================
# 2. Database Module (PostgreSQL / PostGIS)
# ==============================================================================
# TODO (Phase 9.3 Cloud Migration):
# In production cloud deployments, this local StatefulSet module will be replaced
# by a managed database abstraction (e.g. AWS RDS PostgreSQL with Multi-AZ,
# automated backups, and read replicas). The module interface (host, port, name)
# is preserved so compute can connect transparently without code changes.
# ==============================================================================
module "database" {
  source = "../../modules/database"

  namespace       = module.networking.namespace_name
  environment     = var.environment
  postgres_image  = var.postgres_image
  storage_size    = var.postgres_storage_size
  config_map_name = module.networking.config_map_name
  secret_name     = module.networking.secret_name
  cpu_request     = "500m"
  cpu_limit       = "2000m"
  memory_request  = "1Gi"
  memory_limit    = "2Gi"
}

# ==============================================================================
# 3. Cache Module (Redis Streaming Broker)
# ==============================================================================
# TODO (Phase 9.3 Cloud Migration):
# In production cloud deployments, this containerized Redis deployment will be
# replaced by a managed Redis cluster (e.g. AWS ElastiCache Redis replication
# group or GCP Memorystore) with automated failover and multi-AZ replication.
# ==============================================================================
module "cache" {
  source = "../../modules/cache"

  namespace      = module.networking.namespace_name
  environment    = var.environment
  redis_image    = var.redis_image
  cpu_request    = "250m"
  cpu_limit      = "1000m"
  memory_request = "256Mi"
  memory_limit   = "1Gi"
}

# ==============================================================================
# 4. Compute Module (Backend Daphne ASGI & Workers)
# ==============================================================================
module "compute" {
  source = "../../modules/compute"

  namespace                = module.networking.namespace_name
  environment              = var.environment
  config_map_name          = module.networking.config_map_name
  secret_name              = module.networking.secret_name
  backend_image            = var.backend_image
  worker_image             = var.worker_image
  backend_replicas         = var.backend_replicas
  position_worker_replicas = var.position_worker_replicas
  alert_worker_replicas    = var.alert_worker_replicas
  backend_cpu_request      = var.backend_cpu_request
  backend_cpu_limit        = var.backend_cpu_limit
  backend_memory_request   = var.backend_memory_request
  backend_memory_limit     = var.backend_memory_limit
  worker_cpu_request       = var.worker_cpu_request
  worker_cpu_limit         = var.worker_cpu_limit
  worker_memory_request    = var.worker_memory_request
  worker_memory_limit      = var.worker_memory_limit

  depends_on = [
    module.database,
    module.cache,
  ]
}

# ==============================================================================
# 5. Frontend Module (React Nginx Web Tier)
# ==============================================================================
module "frontend" {
  source = "../../modules/frontend"

  namespace         = module.networking.namespace_name
  environment       = var.environment
  frontend_image    = var.frontend_image
  frontend_replicas = var.frontend_replicas
  cpu_request       = "100m"
  cpu_limit         = "500m"
  memory_request    = "128Mi"
  memory_limit      = "256Mi"
}

# ==============================================================================
# 6. Monitoring Module (Prometheus & Grafana)
# ==============================================================================
module "monitoring" {
  source = "../../modules/monitoring"

  namespace            = module.networking.namespace_name
  environment          = var.environment
  backend_service_name = module.compute.backend_service_name
  backend_service_port = module.compute.backend_service_port
  prometheus_image     = var.prometheus_image
  grafana_image        = var.grafana_image

  depends_on = [
    module.compute,
  ]
}
