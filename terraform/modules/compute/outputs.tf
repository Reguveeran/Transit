output "backend_service_name" {
  description = "Backend ClusterIP Service name"
  value       = kubernetes_service.backend_service.metadata[0].name
}

output "backend_service_port" {
  description = "Backend Service port"
  value       = 8000
}

output "worker_deployments" {
  description = "List of worker deployment names"
  value = [
    kubernetes_deployment.worker_position.metadata[0].name,
    kubernetes_deployment.worker_alert.metadata[0].name,
  ]
}
