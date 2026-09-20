# ==============================================================================
# AWS Ingress Module — Variables
# ==============================================================================

variable "environment" {
  description = "Environment identifier"
  type        = string
}

variable "namespace" {
  description = "Kubernetes namespace"
  type        = string
}

variable "public_subnet_ids" {
  description = "Public Subnet IDs for internet-facing ALB placement"
  type        = list(string)
}

variable "alb_security_group_id" {
  description = "Security Group ID for the ALB"
  type        = string
}

variable "frontend_service_name" {
  description = "Frontend Service name"
  type        = string
  default     = "frontend-service"
}

variable "frontend_service_port" {
  description = "Frontend Service port"
  type        = number
  default     = 80
}

variable "backend_service_name" {
  description = "Backend Service name"
  type        = string
  default     = "backend-service"
}

variable "backend_service_port" {
  description = "Backend Service port"
  type        = number
  default     = 8000
}

variable "certificate_arn" {
  description = "ACM TLS Certificate ARN"
  type        = string
  default     = ""
}

variable "enable_tls" {
  description = "Toggle HTTPS listener and TLS redirection"
  type        = bool
  default     = false
}

variable "domain_name" {
  description = "Optional domain name filter for ingress routing"
  type        = string
  default     = ""
}
