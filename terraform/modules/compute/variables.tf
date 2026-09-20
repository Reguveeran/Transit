variable "namespace" {
  description = "Target Kubernetes namespace"
  type        = string
}

variable "environment" {
  description = "Environment identifier (dev, staging, prod)"
  type        = string
}

variable "config_map_name" {
  description = "Application ConfigMap name"
  type        = string
}

variable "secret_name" {
  description = "Application Secret name"
  type        = string
}

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

variable "backend_replicas" {
  description = "Replica count for backend deployment"
  type        = number
  default     = 1
}

variable "position_worker_replicas" {
  description = "Replica count for position worker deployment"
  type        = number
  default     = 1
}

variable "alert_worker_replicas" {
  description = "Replica count for alert worker deployment"
  type        = number
  default     = 1
}

variable "backend_cpu_request" {
  description = "Backend CPU request"
  type        = string
  default     = "100m"
}

variable "backend_cpu_limit" {
  description = "Backend CPU limit"
  type        = string
  default     = "1000m"
}

variable "backend_memory_request" {
  description = "Backend memory request"
  type        = string
  default     = "128Mi"
}

variable "backend_memory_limit" {
  description = "Backend memory limit"
  type        = string
  default     = "1Gi"
}

variable "worker_cpu_request" {
  description = "Worker CPU request"
  type        = string
  default     = "100m"
}

variable "worker_cpu_limit" {
  description = "Worker CPU limit"
  type        = string
  default     = "500m"
}

variable "worker_memory_request" {
  description = "Worker memory request"
  type        = string
  default     = "128Mi"
}

variable "worker_memory_limit" {
  description = "Worker memory limit"
  type        = string
  default     = "512Mi"
}
