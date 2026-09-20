output "ingress_name" {
  description = "Ingress resource name"
  value       = kubernetes_ingress_v1.unitransit.metadata[0].name
}

output "ingress_namespace" {
  description = "Ingress namespace"
  value       = kubernetes_ingress_v1.unitransit.metadata[0].namespace
}
