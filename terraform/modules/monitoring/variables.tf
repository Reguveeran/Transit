variable "namespace" {
  description = "Target Kubernetes namespace"
  type        = string
}

variable "environment" {
  description = "Environment identifier (dev, staging, prod)"
  type        = string
}

variable "backend_service_name" {
  description = "Target backend service name for Prometheus scraping"
  type        = string
}

variable "backend_service_port" {
  description = "Target backend service port for Prometheus scraping"
  type        = number
  default     = 8000
}

variable "prometheus_image" {
  description = "Prometheus container image"
  type        = string
  default     = "prom/prometheus:v2.47.0"
}

variable "grafana_image" {
  description = "Grafana container image"
  type        = string
  default     = "grafana/grafana:10.1.0"
}

variable "cpu_request" {
  description = "CPU request for monitoring pods"
  type        = string
  default     = "50m"
}

variable "memory_request" {
  description = "Memory request for monitoring pods"
  type        = string
  default     = "64Mi"
}
