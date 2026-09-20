# ==============================================================================
# AWS ACM Module — ACM Certificate with DNS Validation
# ==============================================================================

resource "aws_acm_certificate" "cert" {
  count = var.enable_tls && var.domain_name != "" ? 1 : 0

  domain_name               = var.domain_name
  subject_alternative_names = var.subject_alternative_names
  validation_method         = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name        = "unitransit-acm-${var.environment}"
    Environment = var.environment
  }
}
