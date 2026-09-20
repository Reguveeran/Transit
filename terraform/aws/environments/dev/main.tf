provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "UniTransit"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Phase       = "9.3E"
    }
  }
}

# 1. AWS VPC Module (Multi-AZ Subnets & Single NAT Gateway for Dev)
module "vpc" {
  source = "../../modules/vpc"

  vpc_cidr                 = var.vpc_cidr
  environment              = var.environment
  cluster_name             = var.cluster_name
  availability_zones       = ["${var.aws_region}a", "${var.aws_region}b", "${var.aws_region}c"]
  public_subnet_cidrs      = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  private_app_subnet_cidrs = ["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"]
  private_db_subnet_cidrs  = ["10.0.21.0/24", "10.0.22.0/24", "10.0.23.0/24"]
  single_nat_gateway       = true
}

# 2. Security Groups Module (Least-Privilege Micro-Segmentation)
module "security_groups" {
  source = "../../modules/security_groups"

  vpc_id       = module.vpc.vpc_id
  environment  = var.environment
  cluster_name = var.cluster_name
}

# 3. IAM Module (EKS Cluster & Node Group Roles)
module "iam" {
  source = "../../modules/iam"

  environment  = var.environment
  cluster_name = var.cluster_name
}

# 4. EKS Module (Stateless Compute Layer: Control Plane & Managed Node Group)
module "eks" {
  source = "../../modules/eks"

  cluster_name              = var.cluster_name
  environment               = var.environment
  kubernetes_version        = "1.30"
  vpc_id                    = module.vpc.vpc_id
  subnet_ids                = module.vpc.private_app_subnet_ids
  cluster_role_arn          = module.iam.eks_cluster_role_arn
  node_role_arn             = module.iam.eks_nodes_role_arn
  cluster_security_group_id = module.security_groups.eks_cluster_security_group_id
  node_security_group_id    = module.security_groups.eks_nodes_security_group_id
  instance_types            = ["t3.medium"]
  capacity_type             = "ON_DEMAND"
  desired_size              = 2
  min_size                  = 1
  max_size                  = 4
  disk_size                 = 30

  depends_on = [
    module.iam,
    module.vpc,
    module.security_groups,
  ]
}

# 5. RDS Module (Stateful Managed PostgreSQL with PostGIS in Private DB Subnets)
module "rds" {
  source = "../../modules/rds"

  environment             = var.environment
  db_name                 = "unitransit"
  db_username             = "unitransit_admin"
  db_password             = var.db_password
  instance_class          = "db.t4g.medium"
  allocated_storage       = 20
  max_allocated_storage   = 100
  multi_az                = false
  db_subnet_group_name    = module.vpc.db_subnet_group_name
  security_group_id       = module.security_groups.rds_security_group_id
  backup_retention_period = 7
  deletion_protection     = false

  depends_on = [
    module.vpc,
    module.security_groups,
  ]
}

# 6. ElastiCache Module (Stateful Managed Redis Replication Group for Streams)
module "elasticache" {
  source = "../../modules/elasticache"

  environment                = var.environment
  node_type                  = "cache.t4g.small"
  num_cache_clusters         = 1
  engine_version             = "7.1"
  port                       = 6379
  subnet_ids                 = module.vpc.private_db_subnet_ids
  security_group_id          = module.security_groups.elasticache_security_group_id
  automatic_failover_enabled = false
  multi_az_enabled           = false

  depends_on = [
    module.vpc,
    module.security_groups,
  ]
}

# 7. Kubernetes Provider Configuration for EKS
provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    args        = ["eks", "get-token", "--cluster-name", module.eks.cluster_name]
    command     = "aws"
  }
}

# 8. Workloads Module (Stateless Workload Deployments on EKS)
module "workloads" {
  source = "../../modules/workloads"

  environment              = var.environment
  namespace                = "unitransit-${var.environment}"
  backend_image            = var.backend_image
  worker_image             = var.worker_image
  frontend_image           = var.frontend_image
  backend_replicas         = 1
  position_worker_replicas = 1
  alert_worker_replicas    = 1
  frontend_replicas        = 1

  postgres_host     = module.rds.db_address
  postgres_port     = module.rds.db_port
  postgres_db       = module.rds.db_name
  postgres_user     = module.rds.db_username
  postgres_password = var.db_password

  redis_host        = module.elasticache.primary_endpoint_address
  redis_port        = module.elasticache.port
  redis_stream_key  = "transport.events"
  django_secret_key = var.django_secret_key

  backend_resources = {
    cpu_request    = "100m"
    cpu_limit      = "500m"
    memory_request = "128Mi"
    memory_limit   = "512Mi"
  }

  worker_resources = {
    cpu_request    = "100m"
    cpu_limit      = "250m"
    memory_request = "128Mi"
    memory_limit   = "256Mi"
  }

  frontend_resources = {
    cpu_request    = "50m"
    cpu_limit      = "100m"
    memory_request = "64Mi"
    memory_limit   = "128Mi"
  }

  depends_on = [
    module.eks,
    module.rds,
    module.elasticache,
  ]
}

# 9. AWS Load Balancer Controller Module (IRSA Service Account)
module "alb_controller" {
  source = "../../modules/alb_controller"

  environment       = var.environment
  cluster_name      = var.cluster_name
  oidc_provider_arn = module.eks.oidc_provider_arn
  oidc_issuer_url   = module.eks.oidc_issuer_url

  depends_on = [
    module.eks,
  ]
}

# 10. ACM TLS Certificate Module (Conditional DNS Validation)
module "acm" {
  source = "../../modules/acm"

  environment = var.environment
  domain_name = var.domain_name
  enable_tls  = var.enable_tls
}

# 11. ALB Ingress Module (HTTP/HTTPS Routing & WebSocket Upgrade)
module "ingress" {
  source = "../../modules/ingress"

  environment           = var.environment
  namespace             = module.workloads.namespace
  public_subnet_ids     = module.vpc.public_subnet_ids
  alb_security_group_id = module.security_groups.alb_security_group_id
  frontend_service_name = module.workloads.frontend_service_name
  frontend_service_port = module.workloads.frontend_service_port
  backend_service_name  = module.workloads.backend_service_name
  backend_service_port  = module.workloads.backend_service_port
  certificate_arn       = module.acm.certificate_arn
  enable_tls            = var.enable_tls
  domain_name           = var.domain_name

  depends_on = [
    module.workloads,
    module.alb_controller,
  ]
}

# 12. Route 53 DNS Alias Module (Conditional DNS Record)
module "route53" {
  source = "../../modules/route53"

  enable_dns     = var.enable_dns
  hosted_zone_id = var.hosted_zone_id
  domain_name    = var.domain_name
  alb_dns_name   = "" # Injected post-ALB provisioning
  alb_zone_id    = ""
}
