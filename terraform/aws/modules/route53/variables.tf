# ==============================================================================
# AWS Route 53 Module — Variables
# ==============================================================================

variable "enable_dns" {
  description = "Toggle to manage Route 53 DNS records"
  type        = bool
  default     = false
}

variable "hosted_zone_id" {
  description = "Route 53 Hosted Zone ID"
  type        = string
  default     = ""
}

variable "domain_name" {
  description = "Record domain name (e.g. app.unitransit.example.com)"
  type        = string
  default     = ""
}

variable "alb_dns_name" {
  description = "DNS name of the AWS Application Load Balancer"
  type        = string
  default     = ""
}

variable "alb_zone_id" {
  description = "Canonical Hosted Zone ID of the Application Load Balancer"
  type        = string
  default     = ""
}
