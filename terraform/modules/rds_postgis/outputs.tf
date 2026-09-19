output "endpoint" {
  value       = aws_db_instance.main.endpoint
  description = "RDS connection endpoint"
}

output "address" {
  value       = aws_db_instance.main.address
  description = "RDS database hostname"
}

output "port" {
  value       = aws_db_instance.main.port
  description = "RDS database port"
}
