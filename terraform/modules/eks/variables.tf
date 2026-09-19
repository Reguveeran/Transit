variable "environment" {
  type        = string
  description = "Environment name"
}

variable "subnet_ids" {
  type        = list(string)
  description = "Subnet IDs for EKS"
}

variable "instance_types" {
  type        = list(string)
  default     = ["t3.medium"]
  description = "EC2 instance types for EKS nodes"
}

variable "desired_size" {
  type        = number
  default     = 2
  description = "Desired number of worker nodes"
}

variable "max_size" {
  type        = number
  default     = 5
  description = "Maximum number of worker nodes"
}

variable "min_size" {
  type        = number
  default     = 1
  description = "Minimum number of worker nodes"
}
