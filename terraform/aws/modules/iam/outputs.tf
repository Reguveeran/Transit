output "eks_cluster_role_arn" {
  description = "ARN of the EKS cluster control plane IAM role"
  value       = aws_iam_role.eks_cluster.arn
}

output "eks_cluster_role_name" {
  description = "Name of the EKS cluster control plane IAM role"
  value       = aws_iam_role.eks_cluster.name
}

output "eks_nodes_role_arn" {
  description = "ARN of the EKS worker node group IAM role"
  value       = aws_iam_role.eks_nodes.arn
}

output "eks_nodes_role_name" {
  description = "Name of the EKS worker node group IAM role"
  value       = aws_iam_role.eks_nodes.name
}
