output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "Public Subnet IDs"
  value       = module.vpc.public_subnet_ids
}

output "private_app_subnet_ids" {
  description = "Private App Subnet IDs for EKS"
  value       = module.vpc.private_app_subnet_ids
}

output "private_db_subnet_ids" {
  description = "Private DB Subnet IDs for RDS and ElastiCache"
  value       = module.vpc.private_db_subnet_ids
}

output "db_subnet_group_name" {
  description = "Database Subnet Group Name"
  value       = module.vpc.db_subnet_group_name
}

output "security_groups" {
  description = "Security Group IDs"
  value = {
    alb         = module.security_groups.alb_security_group_id
    eks_cluster = module.security_groups.eks_cluster_security_group_id
    eks_nodes   = module.security_groups.eks_nodes_security_group_id
    rds         = module.security_groups.rds_security_group_id
    elasticache = module.security_groups.elasticache_security_group_id
  }
}

output "iam_roles" {
  description = "IAM Role ARNs for EKS"
  value = {
    eks_cluster_role_arn    = module.iam.eks_cluster_role_arn
    eks_nodes_role_arn      = module.iam.eks_nodes_role_arn
    alb_controller_role_arn = module.alb_controller.iam_role_arn
  }
}

output "eks_cluster" {
  description = "EKS Cluster connection parameters"
  value = {
    cluster_id        = module.eks.cluster_id
    cluster_name      = module.eks.cluster_name
    cluster_endpoint  = module.eks.cluster_endpoint
    cluster_version   = module.eks.cluster_version
    oidc_provider_arn = module.eks.oidc_provider_arn
  }
}

output "rds_postgres" {
  description = "RDS PostgreSQL database connection parameters"
  value = {
    db_endpoint = module.rds.db_endpoint
    db_address  = module.rds.db_address
    db_port     = module.rds.db_port
    db_name     = module.rds.db_name
    db_username = module.rds.db_username
  }
}

output "elasticache_redis" {
  description = "ElastiCache Redis streaming cluster parameters"
  value = {
    primary_endpoint_address = module.elasticache.primary_endpoint_address
    reader_endpoint_address  = module.elasticache.reader_endpoint_address
    port                     = module.elasticache.port
  }
}

output "workloads" {
  description = "Deployed EKS Workloads metadata"
  value = {
    namespace             = module.workloads.namespace
    backend_service_name  = module.workloads.backend_service_name
    backend_service_port  = module.workloads.backend_service_port
    frontend_service_name = module.workloads.frontend_service_name
    frontend_service_port = module.workloads.frontend_service_port
    config_map_name       = module.workloads.config_map_name
    secret_name           = module.workloads.secret_name
  }
}

output "ingress" {
  description = "Application Ingress and TLS metadata"
  value = {
    ingress_name      = module.ingress.ingress_name
    ingress_namespace = module.ingress.ingress_namespace
    alb_controller_sa = module.alb_controller.service_account_name
    certificate_arn   = module.acm.certificate_arn
    dns_fqdn          = module.route53.fqdn
  }
}
