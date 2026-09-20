# ==============================================================================
# AWS ACM Module — TLS Certificate Variables
# ==============================================================================

variable "environment" {
  description = "Environment identifier"
  type        = string
}

variable "domain_name" {
  description = "Domain name for ACM Certificate (e.g. app.unitransit.internal / api.example.com)"
  type        = string
  default     = ""
}

variable "enable_tls" {
  description = "Toggle to provision ACM TLS Certificate"
  type        = bool
  default     = false
}

variable "subject_alternative_names" {
  description = "Additional domain names to include in the certificate"
  type        = list(string)
  default     = []
}
