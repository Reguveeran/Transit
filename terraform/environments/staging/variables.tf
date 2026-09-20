variable "kubeconfig_path" {
  description = "Path to local kubeconfig"
  type        = string
  default     = "~/.kube/config"
}

variable "kubeconfig_context" {
  description = "Kubernetes context to target"
  type        = string
  default     = "docker-desktop"
}

variable "environment" {
  description = "Deployment environment name"
  type        = string
  default     = "staging"
}

variable "namespace" {
  description = "Kubernetes namespace"
  type        = string
  default     = "unitransit-staging"
}

# Image parameters
variable "backend_image" {
  description = "Backend container image"
  type        = string
  default     = "unitransit/backend:latest"
}

variable "worker_image" {
  description = "Worker container image"
  type        = string
  default     = "unitransit/worker:latest"
}

variable "frontend_image" {
  description = "Frontend container image"
  type        = string
  default     = "unitransit/frontend:latest"
}

variable "redis_image" {
  description = "Redis container image"
  type        = string
  default     = "redis:7-alpine"
}

variable "postgres_image" {
  description = "PostgreSQL container image"
  type        = string
  default     = "postgis/postgis:15-3.3-alpine"
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

# Replica parameters
variable "backend_replicas" {
  description = "Backend replica count"
  type        = number
  default     = 2
}

variable "position_worker_replicas" {
  description = "Position worker replica count"
  type        = number
  default     = 2
}

variable "alert_worker_replicas" {
  description = "Alert worker replica count"
  type        = number
  default     = 1
}

variable "frontend_replicas" {
  description = "Frontend replica count"
  type        = number
  default     = 2
}

# Resource parameters
variable "backend_cpu_request" {
  description = "Backend CPU request"
  type        = string
  default     = "200m"
}

variable "backend_cpu_limit" {
  description = "Backend CPU limit"
  type        = string
  default     = "1000m"
}

variable "backend_memory_request" {
  description = "Backend memory request"
  type        = string
  default     = "256Mi"
}

variable "backend_memory_limit" {
  description = "Backend memory limit"
  type        = string
  default     = "1Gi"
}

variable "worker_cpu_request" {
  description = "Worker CPU request"
  type        = string
  default     = "150m"
}

variable "worker_cpu_limit" {
  description = "Worker CPU limit"
  type        = string
  default     = "500m"
}

variable "worker_memory_request" {
  description = "Worker memory request"
  type        = string
  default     = "256Mi"
}

variable "worker_memory_limit" {
  description = "Worker memory limit"
  type        = string
  default     = "512Mi"
}

variable "postgres_storage_size" {
  description = "PostgreSQL PVC storage size"
  type        = string
  default     = "10Gi"
}

variable "postgres_db" {
  description = "Database name"
  type        = string
  default     = "unitransit"
}

variable "postgres_user" {
  description = "Database user"
  type        = string
  default     = "unitransit"
}

variable "postgres_password" {
  description = "Database password"
  type        = string
  sensitive   = true
  default     = "unitransit_staging_secure_password"
}

variable "secret_key" {
  description = "Django secret key"
  type        = string
  sensitive   = true
  default     = "unitransit-staging-secret-key-2026-modular-stack"
}
