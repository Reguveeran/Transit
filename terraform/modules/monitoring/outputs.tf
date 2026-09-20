output "prometheus_service_name" {
  description = "Prometheus Service name"
  value       = kubernetes_service.prometheus_service.metadata[0].name
}

output "grafana_service_name" {
  description = "Grafana Service name"
  value       = kubernetes_service.grafana_service.metadata[0].name
}
