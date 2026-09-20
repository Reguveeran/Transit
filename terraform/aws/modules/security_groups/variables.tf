variable "vpc_id" {
  description = "VPC ID where security groups will be created"
  type        = string
}

variable "environment" {
  description = "Deployment environment identifier"
  type        = string
}

variable "cluster_name" {
  description = "EKS cluster identifier"
  type        = string
  default     = "unitransit-eks"
}
