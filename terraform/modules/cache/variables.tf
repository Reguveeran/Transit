variable "namespace" {
  description = "Target Kubernetes namespace"
  type        = string
}

variable "environment" {
  description = "Environment identifier (dev, staging, prod)"
  type        = string
}

variable "redis_image" {
  description = "Redis container image"
  type        = string
  default     = "redis:7-alpine"
}

variable "cpu_request" {
  description = "CPU request for Redis"
  type        = string
  default     = "100m"
}

variable "cpu_limit" {
  description = "CPU limit for Redis"
  type        = string
  default     = "500m"
}

variable "memory_request" {
  description = "Memory request for Redis"
  type        = string
  default     = "128Mi"
}

variable "memory_limit" {
  description = "Memory limit for Redis"
  type        = string
  default     = "512Mi"
}
