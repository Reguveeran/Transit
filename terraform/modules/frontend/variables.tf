variable "namespace" {
  description = "Target Kubernetes namespace"
  type        = string
}

variable "environment" {
  description = "Environment identifier (dev, staging, prod)"
  type        = string
}

variable "frontend_image" {
  description = "Frontend container image"
  type        = string
  default     = "unitransit/frontend:latest"
}

variable "frontend_replicas" {
  description = "Replica count for frontend deployment"
  type        = number
  default     = 1
}

variable "cpu_request" {
  description = "CPU request for frontend"
  type        = string
  default     = "50m"
}

variable "cpu_limit" {
  description = "CPU limit for frontend"
  type        = string
  default     = "250m"
}

variable "memory_request" {
  description = "Memory request for frontend"
  type        = string
  default     = "64Mi"
}

variable "memory_limit" {
  description = "Memory limit for frontend"
  type        = string
  default     = "128Mi"
}
