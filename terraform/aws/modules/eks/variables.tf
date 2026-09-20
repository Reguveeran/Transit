variable "cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
  default     = "unitransit-eks"
}

variable "environment" {
  description = "Deployment environment identifier"
  type        = string
}

variable "kubernetes_version" {
  description = "Desired Kubernetes version for EKS control plane"
  type        = string
  default     = "1.30"
}

variable "vpc_id" {
  description = "VPC ID where EKS will be deployed"
  type        = string
}

variable "subnet_ids" {
  description = "Subnet IDs for EKS control plane and worker nodes (Private App Subnets)"
  type        = list(string)
}

variable "cluster_role_arn" {
  description = "IAM Role ARN for the EKS control plane"
  type        = string
}

variable "node_role_arn" {
  description = "IAM Role ARN for EKS managed worker nodes"
  type        = string
}

variable "cluster_security_group_id" {
  description = "Security group ID for EKS control plane"
  type        = string
}

variable "node_security_group_id" {
  description = "Security group ID for EKS worker nodes"
  type        = string
}

variable "instance_types" {
  description = "EC2 instance types for EKS worker nodes"
  type        = list(string)
  default     = ["t3.medium"]
}

variable "capacity_type" {
  description = "Type of capacity associated with the EKS Node Group (ON_DEMAND or SPOT)"
  type        = string
  default     = "ON_DEMAND"
}

variable "desired_size" {
  description = "Desired number of worker nodes in node group"
  type        = number
  default     = 2
}

variable "min_size" {
  description = "Minimum number of worker nodes in node group"
  type        = number
  default     = 1
}

variable "max_size" {
  description = "Maximum number of worker nodes in node group"
  type        = number
  default     = 5
}

variable "disk_size" {
  description = "Root EBS volume size in GiB for each worker node"
  type        = number
  default     = 30
}
