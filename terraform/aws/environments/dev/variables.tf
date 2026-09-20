variable "aws_region" {
  description = "AWS deployment region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment identifier"
  type        = string
  default     = "dev"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "cluster_name" {
  description = "EKS Cluster Name"
  type        = string
  default     = "unitransit-dev-eks"
}

variable "db_password" {
  description = "Master password for PostgreSQL database"
  type        = string
  sensitive   = true
  default     = "unitransit_dev_rds_secure_pwd_2026"
}

variable "django_secret_key" {
  description = "Django secret key"
  type        = string
  sensitive   = true
  default     = "django-insecure-dev-secret-key-unitransit-2026"
}

variable "backend_image" {
  description = "Immutable container image for backend"
  type        = string
  default     = "ghcr.io/reguveeran/unitransit-backend:8916745"
}

variable "worker_image" {
  description = "Immutable container image for workers"
  type        = string
  default     = "ghcr.io/reguveeran/unitransit-worker:8916745"
}

variable "frontend_image" {
  description = "Immutable container image for frontend"
  type        = string
  default     = "ghcr.io/reguveeran/unitransit-frontend:8916745"
}

variable "enable_ingress" {
  description = "Toggle to provision ALB Ingress"
  type        = bool
  default     = true
}

variable "enable_tls" {
  description = "Toggle HTTPS listener and ACM TLS Certificate"
  type        = bool
  default     = false
}

variable "enable_dns" {
  description = "Toggle Route 53 DNS record management"
  type        = bool
  default     = false
}

variable "domain_name" {
  description = "Custom domain name (leave blank if no domain configured)"
  type        = string
  default     = ""
}

variable "hosted_zone_id" {
  description = "Route 53 Hosted Zone ID"
  type        = string
  default     = ""
}
