# ==============================================================================
# AWS EKS Workloads Module — Outputs
# ==============================================================================

output "namespace" {
  description = "Kubernetes namespace for UniTransit workloads"
  value       = kubernetes_namespace.unitransit.metadata[0].name
}

output "backend_service_name" {
  description = "Backend ClusterIP Service name"
  value       = kubernetes_service.backend_service.metadata[0].name
}

output "backend_service_port" {
  description = "Backend Service port"
  value       = kubernetes_service.backend_service.spec[0].port[0].port
}

output "frontend_service_name" {
  description = "Frontend ClusterIP Service name"
  value       = kubernetes_service.frontend_service.metadata[0].name
}

output "frontend_service_port" {
  description = "Frontend Service port"
  value       = kubernetes_service.frontend_service.spec[0].port[0].port
}

output "config_map_name" {
  description = "Application ConfigMap name"
  value       = kubernetes_config_map.unitransit_config.metadata[0].name
}

output "secret_name" {
  description = "Application Secret name"
  value       = kubernetes_secret.unitransit_secrets.metadata[0].name
}
