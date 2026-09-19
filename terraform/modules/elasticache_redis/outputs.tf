output "primary_endpoint_address" {
  value       = aws_elasticache_replication_group.main.primary_endpoint_address
  description = "Redis primary endpoint hostname"
}

output "port" {
  value       = aws_elasticache_replication_group.main.port
  description = "Redis port"
}
