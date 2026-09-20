variable "namespace" {
  description = "Target Kubernetes namespace"
  type        = string
}

variable "environment" {
  description = "Environment identifier (dev, staging, prod)"
  type        = string
}

variable "postgres_image" {
  description = "PostgreSQL Docker image with PostGIS"
  type        = string
  default     = "postgis/postgis:15-3.3-alpine"
}

variable "storage_size" {
  description = "Storage request for PostgreSQL PVC"
  type        = string
  default     = "5Gi"
}

variable "config_map_name" {
  description = "Name of the ConfigMap containing database configuration"
  type        = string
}

variable "secret_name" {
  description = "Name of the Secret containing database credentials"
  type        = string
}

variable "cpu_request" {
  description = "CPU request for PostgreSQL"
  type        = string
  default     = "100m"
}

variable "cpu_limit" {
  description = "CPU limit for PostgreSQL"
  type        = string
  default     = "1000m"
}

variable "memory_request" {
  description = "Memory request for PostgreSQL"
  type        = string
  default     = "128Mi"
}

variable "memory_limit" {
  description = "Memory limit for PostgreSQL"
  type        = string
  default     = "1Gi"
}
