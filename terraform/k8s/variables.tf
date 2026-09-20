variable "namespace" {
  description = "Target Kubernetes namespace for Terraform-managed IaC stack"
  type        = string
  default     = "unitransit-iac"
}

variable "kubeconfig_path" {
  description = "Path to local kubeconfig file"
  type        = string
  default     = "~/.kube/config"
}

variable "kubeconfig_context" {
  description = "Kubernetes context to target"
  type        = string
  default     = "docker-desktop"
}

# Application Replicas
variable "backend_replicas" {
  description = "Number of backend pod replicas"
  type        = number
  default     = 1
}

variable "frontend_replicas" {
  description = "Number of frontend pod replicas"
  type        = number
  default     = 1
}

variable "position_worker_replicas" {
  description = "Number of position worker pod replicas"
  type        = number
  default     = 1
}

variable "alert_worker_replicas" {
  description = "Number of alert worker pod replicas"
  type        = number
  default     = 1
}

# Container Images (Preserving local cached & Git-SHA immutable tags)
variable "backend_image" {
  description = "Docker image for UniTransit backend"
  type        = string
  default     = "unitransit/backend:latest"
}

variable "frontend_image" {
  description = "Docker image for UniTransit frontend"
  type        = string
  default     = "unitransit/frontend:latest"
}

variable "worker_image" {
  description = "Docker image for UniTransit background workers"
  type        = string
  default     = "unitransit/worker:latest"
}

variable "redis_image" {
  description = "Docker image for Redis stream broker"
  type        = string
  default     = "redis:7-alpine"
}

variable "postgres_image" {
  description = "Docker image for PostgreSQL with PostGIS extension"
  type        = string
  default     = "postgis/postgis:15-3.3-alpine"
}

variable "prometheus_image" {
  description = "Docker image for Prometheus telemetry scraper"
  type        = string
  default     = "prom/prometheus:v2.47.0"
}

variable "grafana_image" {
  description = "Docker image for Grafana telemetry dashboard"
  type        = string
  default     = "grafana/grafana:10.1.0"
}

# Database & Application Secrets
variable "postgres_db" {
  description = "Database name for PostgreSQL"
  type        = string
  default     = "unitransit"
}

variable "postgres_user" {
  description = "Database user for PostgreSQL"
  type        = string
  default     = "unitransit"
}

variable "postgres_password" {
  description = "Password for PostgreSQL user"
  type        = string
  default     = "unitransit_iac_secure_password"
  sensitive   = true
}

variable "secret_key" {
  description = "Django secret key"
  type        = string
  default     = "unitransit-iac-secret-key-2026-reproducible-stack"
  sensitive   = true
}
