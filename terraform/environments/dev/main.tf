terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

module "vpc" {
  source      = "../../modules/vpc"
  environment = "dev"
  cidr_block  = "10.10.0.0/16"
}

module "eks" {
  source         = "../../modules/eks"
  environment    = "dev"
  subnet_ids     = module.vpc.private_subnet_ids
  instance_types = ["t3.medium"]
  desired_size   = 2
  min_size       = 1
  max_size       = 3
}

module "rds" {
  source         = "../../modules/rds_postgis"
  environment    = "dev"
  vpc_id         = module.vpc.vpc_id
  vpc_cidr       = "10.10.0.0/16"
  subnet_ids     = module.vpc.private_subnet_ids
  instance_class = "db.t3.medium"
  db_password    = var.db_password
}

module "redis" {
  source      = "../../modules/elasticache_redis"
  environment = "dev"
  vpc_id      = module.vpc.vpc_id
  vpc_cidr    = "10.10.0.0/16"
  subnet_ids  = module.vpc.private_subnet_ids
  node_type   = "cache.t3.micro"
}
