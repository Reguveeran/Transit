variable "environment" {
  description = "Deployment environment identifier"
  type        = string
}

variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
  default     = "unitransit-eks"
}
