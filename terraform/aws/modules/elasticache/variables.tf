variable "environment" {
  description = "Deployment environment identifier (dev, prod)"
  type        = string
}

variable "node_type" {
  description = "ElastiCache Redis instance type"
  type        = string
  default     = "cache.t4g.small"
}

variable "num_cache_clusters" {
  description = "Number of cache clusters (nodes) in the replication group"
  type        = number
  default     = 1
}

variable "engine_version" {
  description = "Redis engine version (Redis Streams supported on >= 5.0, optimal 7.1)"
  type        = string
  default     = "7.1"
}

variable "port" {
  description = "Redis port"
  type        = number
  default     = 6379
}

variable "subnet_ids" {
  description = "List of private database subnet IDs for ElastiCache Subnet Group"
  type        = list(string)
}

variable "security_group_id" {
  description = "Security group ID allowing inbound port 6379 strictly from EKS worker nodes"
  type        = string
}

variable "automatic_failover_enabled" {
  description = "Specifies whether a read-only replica will be automatically promoted to read/write primary if the primary node fails"
  type        = bool
  default     = false
}

variable "multi_az_enabled" {
  description = "Specifies whether Multi-AZ is enabled for the replication group"
  type        = bool
  default     = false
}

variable "transit_encryption_enabled" {
  description = "Enable TLS in-transit encryption"
  type        = bool
  default     = true
}

variable "at_rest_encryption_enabled" {
  description = "Enable KMS at-rest encryption"
  type        = bool
  default     = true
}
