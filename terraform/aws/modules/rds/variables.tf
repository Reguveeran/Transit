variable "environment" {
  description = "Deployment environment identifier (dev, prod)"
  type        = string
}

variable "db_name" {
  description = "Name of the default database to create"
  type        = string
  default     = "unitransit"
}

variable "db_username" {
  description = "Master username for PostgreSQL"
  type        = string
  default     = "unitransit_admin"
}

variable "db_password" {
  description = "Master password for PostgreSQL"
  type        = string
  sensitive   = true
}

variable "instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t4g.medium"
}

variable "allocated_storage" {
  description = "Allocated storage in GiB"
  type        = number
  default     = 20
}

variable "max_allocated_storage" {
  description = "Maximum storage limit in GiB for autoscaling"
  type        = number
  default     = 100
}

variable "engine_version" {
  description = "PostgreSQL engine version"
  type        = string
  default     = "15.7"
}

variable "multi_az" {
  description = "Specifies if the RDS instance is multi-AZ"
  type        = bool
  default     = false
}

variable "db_subnet_group_name" {
  description = "Name of the DB subnet group in private DB subnets"
  type        = string
}

variable "security_group_id" {
  description = "Security group ID allowing inbound port 5432 from EKS worker nodes"
  type        = string
}

variable "backup_retention_period" {
  description = "Days to retain automated backups"
  type        = number
  default     = 7
}

variable "deletion_protection" {
  description = "If the DB instance should have deletion protection enabled"
  type        = bool
  default     = false
}
