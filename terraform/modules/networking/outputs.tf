output "namespace_name" {
  description = "Name of the provisioned Kubernetes namespace"
  value       = kubernetes_namespace.env_namespace.metadata[0].name
}

output "config_map_name" {
  description = "Name of the application ConfigMap"
  value       = kubernetes_config_map.unitransit_config.metadata[0].name
}

output "secret_name" {
  description = "Name of the application Secret"
  value       = kubernetes_secret.unitransit_secrets.metadata[0].name
}
