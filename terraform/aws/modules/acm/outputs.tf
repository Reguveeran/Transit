output "certificate_arn" {
  description = "ARN of the ACM TLS Certificate"
  value       = try(aws_acm_certificate.cert[0].arn, "")
}

output "domain_validation_options" {
  description = "DNS validation options for Route 53 or third-party DNS"
  value       = try(aws_acm_certificate.cert[0].domain_validation_options, [])
}
