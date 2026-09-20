output "service_name" {
  description = "Redis Service name"
  value       = kubernetes_service.redis_service.metadata[0].name
}

output "service_port" {
  description = "Redis Service port"
  value       = 6379
}

output "redis_host" {
  description = "Redis hostname in cluster"
  value       = "${kubernetes_service.redis_service.metadata[0].name}.${var.namespace}.svc.cluster.local"
}
