# ==============================================================================
# AWS Route 53 Module — Alias DNS Record pointing to ALB
# ==============================================================================

resource "aws_route53_record" "app" {
  count = var.enable_dns && var.hosted_zone_id != "" && var.domain_name != "" && var.alb_dns_name != "" ? 1 : 0

  zone_id = var.hosted_zone_id
  name    = var.domain_name
  type    = "A"

  alias {
    name                   = var.alb_dns_name
    zone_id                = var.alb_zone_id
    evaluate_target_health = true
  }
}
