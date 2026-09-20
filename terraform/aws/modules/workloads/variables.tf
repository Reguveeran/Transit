# ==============================================================================
# AWS EKS Workloads Module — Variables
# ==============================================================================

variable "environment" {
  description = "Deployment environment (dev, staging, prod)"
  type        = string
}

variable "namespace" {
  description = "Kubernetes namespace for UniTransit EKS workloads"
  type        = string
}

# --- Image References (Immutable GHCR Tags or Cryptographic SHA Digests) ---

variable "backend_image" {
  description = "Container image reference for backend (immutable Git SHA or SHA-256 digest)"
  type        = string
}

variable "worker_image" {
  description = "Container image reference for workers (immutable Git SHA or SHA-256 digest)"
  type        = string
}

variable "frontend_image" {
  description = "Container image reference for frontend (immutable Git SHA or SHA-256 digest)"
  type        = string
}

# --- Sizing & Replica Configuration ---

variable "backend_replicas" {
  description = "Number of backend Daphne ASGI replicas"
  type        = number
  default     = 1
}

variable "position_worker_replicas" {
  description = "Number of PositionWorker replicas"
  type        = number
  default     = 1
}

variable "alert_worker_replicas" {
  description = "Number of AlertWorker replicas"
  type        = number
  default     = 1
}

variable "frontend_replicas" {
  description = "Number of frontend Nginx replicas"
  type        = number
  default     = 1
}

# --- Resource Requests & Limits ---

variable "backend_resources" {
  description = "Resource requests and limits for backend"
  type = object({
    cpu_request    = string
    cpu_limit      = string
    memory_request = string
    memory_limit   = string
  })
  default = {
    cpu_request    = "100m"
    cpu_limit      = "500m"
    memory_request = "128Mi"
    memory_limit   = "512Mi"
  }
}

variable "worker_resources" {
  description = "Resource requests and limits for workers"
  type = object({
    cpu_request    = string
    cpu_limit      = string
    memory_request = string
    memory_limit   = string
  })
  default = {
    cpu_request    = "100m"
    cpu_limit      = "250m"
    memory_request = "128Mi"
    memory_limit   = "256Mi"
  }
}

variable "frontend_resources" {
  description = "Resource requests and limits for frontend"
  type = object({
    cpu_request    = string
    cpu_limit      = string
    memory_request = string
    memory_limit   = string
  })
  default = {
    cpu_request    = "50m"
    cpu_limit      = "100m"
    memory_request = "64Mi"
    memory_limit   = "128Mi"
  }
}

# --- Managed Data Tier Integration (Decoupled from RDS & ElastiCache) ---

variable "postgres_host" {
  description = "RDS PostgreSQL endpoint address"
  type        = string
}

variable "postgres_port" {
  description = "RDS PostgreSQL port"
  type        = number
  default     = 5432
}

variable "postgres_db" {
  description = "PostgreSQL database name"
  type        = string
  default     = "unitransit"
}

variable "postgres_user" {
  description = "PostgreSQL username"
  type        = string
  default     = "unitransit_admin"
}

variable "postgres_password" {
  description = "PostgreSQL master password"
  type        = string
  sensitive   = true
}

variable "redis_host" {
  description = "ElastiCache Redis primary endpoint address"
  type        = string
}

variable "redis_port" {
  description = "ElastiCache Redis port"
  type        = number
  default     = 6379
}

variable "redis_stream_key" {
  description = "Redis Stream key for vehicle position events"
  type        = string
  default     = "transport.events"
}

variable "django_secret_key" {
  description = "Django secret key"
  type        = string
  sensitive   = true
  default     = "django-insecure-aws-eks-production-key-change-me"
}
