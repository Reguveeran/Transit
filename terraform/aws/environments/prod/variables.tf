variable "aws_region" {
  description = "AWS deployment region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment identifier"
  type        = string
  default     = "prod"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.100.0.0/16"
}

variable "cluster_name" {
  description = "EKS Cluster Name"
  type        = string
  default     = "unitransit-prod-eks"
}

variable "db_password" {
  description = "Master password for PostgreSQL database"
  type        = string
  sensitive   = true
  default     = "unitransit_prod_rds_secure_pwd_2026"
}

variable "django_secret_key" {
  description = "Django secret key"
  type        = string
  sensitive   = true
  default     = "django-insecure-prod-secret-key-unitransit-2026"
}

variable "backend_image" {
  description = "Immutable cryptographic digest container image for backend"
  type        = string
  default     = "ghcr.io/reguveeran/unitransit-backend@sha256:7be9f178dfdb211b8f14acde4ffcf3665a3c051261cb2841accd06c9a38541e2"
}

variable "worker_image" {
  description = "Immutable cryptographic digest container image for workers"
  type        = string
  default     = "ghcr.io/reguveeran/unitransit-worker@sha256:7be9f178dfdb211b8f14acde4ffcf3665a3c051261cb2841accd06c9a38541e2"
}

variable "frontend_image" {
  description = "Immutable cryptographic digest container image for frontend"
  type        = string
  default     = "ghcr.io/reguveeran/unitransit-frontend@sha256:e9649216e17ad342130fffa0014ad3eb2ba3473ba772e293a38a7c29be0ecf62"
}

variable "backend_replicas" {
  description = "Number of backend Daphne ASGI replicas"
  type        = number
  default     = 3
}

variable "position_worker_replicas" {
  description = "Number of PositionWorker replicas"
  type        = number
  default     = 2
}

variable "alert_worker_replicas" {
  description = "Number of AlertWorker replicas"
  type        = number
  default     = 2
}

variable "frontend_replicas" {
  description = "Number of frontend Nginx replicas"
  type        = number
  default     = 2
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
