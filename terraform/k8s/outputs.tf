output "namespace" {
  description = "Target Kubernetes namespace managed by Terraform"
  value       = kubernetes_namespace.unitransit_iac.metadata[0].name
}

output "backend_service" {
  description = "Backend API service name in unitransit-iac"
  value       = kubernetes_service.backend_service.metadata[0].name
}

output "frontend_service" {
  description = "Frontend Web UI service name in unitransit-iac"
  value       = kubernetes_service.frontend_service.metadata[0].name
}

output "redis_service" {
  description = "Redis stream broker service name in unitransit-iac"
  value       = kubernetes_service.redis_service.metadata[0].name
}

output "postgres_service" {
  description = "PostgreSQL database service name in unitransit-iac"
  value       = kubernetes_service.postgres_service.metadata[0].name
}

output "worker_deployments" {
  description = "Background worker deployment names in unitransit-iac"
  value = [
    kubernetes_deployment.worker_position.metadata[0].name,
    kubernetes_deployment.worker_alert.metadata[0].name,
  ]
}

output "monitoring_services" {
  description = "Prometheus and Grafana service names in unitransit-iac"
  value = {
    prometheus = kubernetes_service.prometheus_service.metadata[0].name
    grafana    = kubernetes_service.grafana_service.metadata[0].name
  }
}
