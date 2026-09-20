variable "namespace" {
  description = "Target Kubernetes namespace"
  type        = string
}

variable "environment" {
  description = "Environment identifier (dev, staging, prod)"
  type        = string
}

variable "app_name" {
  description = "Application label"
  type        = string
  default     = "unitransit"
}

variable "debug" {
  description = "Django debug setting"
  type        = string
  default     = "False"
}

variable "allowed_hosts" {
  description = "Allowed hosts for Django"
  type        = string
  default     = "*"
}

variable "postgres_db" {
  description = "PostgreSQL database name"
  type        = string
  default     = "unitransit"
}

variable "postgres_host" {
  description = "PostgreSQL service host"
  type        = string
  default     = "postgres-service"
}

variable "postgres_port" {
  description = "PostgreSQL service port"
  type        = number
  default     = 5432
}

variable "postgres_user" {
  description = "PostgreSQL database user"
  type        = string
  default     = "unitransit"
}

variable "postgres_password" {
  description = "PostgreSQL database password"
  type        = string
  sensitive   = true
  default     = "unitransit_secure_password"
}

variable "secret_key" {
  description = "Django secret key"
  type        = string
  sensitive   = true
  default     = "unitransit-modular-secret-key-2026"
}

variable "redis_host" {
  description = "Redis service host"
  type        = string
  default     = "redis-service"
}

variable "redis_port" {
  description = "Redis service port"
  type        = number
  default     = 6379
}

variable "redis_stream_key" {
  description = "Redis stream key"
  type        = string
  default     = "transport.events"
}

variable "redis_group_name" {
  description = "Redis consumer group name"
  type        = string
  default     = "unitransit_workers"
}
