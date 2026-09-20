output "iam_role_arn" {
  description = "IAM Role ARN for AWS Load Balancer Controller"
  value       = aws_iam_role.alb_controller.arn
}

output "iam_policy_arn" {
  description = "IAM Policy ARN for AWS Load Balancer Controller"
  value       = aws_iam_policy.alb_controller.arn
}

output "service_account_name" {
  description = "Service Account name"
  value       = kubernetes_service_account.alb_controller.metadata[0].name
}

output "service_account_namespace" {
  description = "Service Account namespace"
  value       = kubernetes_service_account.alb_controller.metadata[0].namespace
}
