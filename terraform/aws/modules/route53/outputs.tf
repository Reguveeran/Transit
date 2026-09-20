output "fqdn" {
  description = "Fully qualified domain name of the Route 53 alias record"
  value       = try(aws_route53_record.app[0].fqdn, "")
}
