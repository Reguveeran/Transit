output "namespace" {
  description = "Target Kubernetes namespace"
  value       = module.networking.namespace_name
}

output "backend_service" {
  description = "Backend API ClusterIP service name"
  value       = module.compute.backend_service_name
}

output "frontend_service" {
  description = "Frontend Web UI service name"
  value       = module.frontend.service_name
}

output "redis_service" {
  description = "Redis stream broker service name"
  value       = module.cache.service_name
}

output "postgres_service" {
  description = "PostgreSQL database service name"
  value       = module.database.service_name
}

output "worker_deployments" {
  description = "Background worker deployment names"
  value       = module.compute.worker_deployments
}

output "monitoring_services" {
  description = "Prometheus and Grafana service names"
  value = {
    prometheus = module.monitoring.prometheus_service_name
    grafana    = module.monitoring.grafana_service_name
  }
}
