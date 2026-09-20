output "service_name" {
  description = "PostgreSQL Service name"
  value       = kubernetes_service.postgres_service.metadata[0].name
}

output "service_port" {
  description = "PostgreSQL Service port"
  value       = 5432
}

output "database_host" {
  description = "PostgreSQL hostname in cluster"
  value       = "${kubernetes_service.postgres_service.metadata[0].name}.${var.namespace}.svc.cluster.local"
}

output "database_name" {
  description = "Database name"
  value       = "unitransit"
}
