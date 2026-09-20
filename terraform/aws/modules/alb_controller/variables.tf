# ==============================================================================
# AWS Load Balancer Controller Module — IRSA & Service Account
# ==============================================================================

variable "environment" {
  description = "Environment identifier"
  type        = string
}

variable "cluster_name" {
  description = "EKS Cluster Name"
  type        = string
}

variable "oidc_provider_arn" {
  description = "ARN of the EKS OIDC Provider for IRSA"
  type        = string
}

variable "oidc_issuer_url" {
  description = "OIDC Issuer URL of the EKS Cluster"
  type        = string
}

variable "namespace" {
  description = "Kubernetes namespace for the AWS Load Balancer Controller"
  type        = string
  default     = "kube-system"
}

variable "service_account_name" {
  description = "Name of the Kubernetes Service Account"
  type        = string
  default     = "aws-load-balancer-controller"
}
