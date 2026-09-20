output "service_name" {
  description = "Frontend Service name"
  value       = kubernetes_service.frontend_service.metadata[0].name
}

output "service_port" {
  description = "Frontend Service port"
  value       = 80
}
