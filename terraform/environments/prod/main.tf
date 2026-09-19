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
  source               = "../../modules/vpc"
  environment          = "prod"
  cidr_block           = "10.20.0.0/16"
  public_subnet_cidrs  = ["10.20.1.0/24", "10.20.2.0/24", "10.20.3.0/24"]
  private_subnet_cidrs = ["10.20.10.0/24", "10.20.11.0/24", "10.20.12.0/24"]
  availability_zones   = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

module "eks" {
  source         = "../../modules/eks"
  environment    = "prod"
  subnet_ids     = module.vpc.private_subnet_ids
  instance_types = ["m5.large", "c5.large"]
  desired_size   = 4
  min_size       = 3
  max_size       = 12
}

module "rds" {
  source         = "../../modules/rds_postgis"
  environment    = "prod"
  vpc_id         = module.vpc.vpc_id
  vpc_cidr       = "10.20.0.0/16"
  subnet_ids     = module.vpc.private_subnet_ids
  instance_class = "db.m5.xlarge"
  db_password    = var.db_password
}

module "redis" {
  source             = "../../modules/elasticache_redis"
  environment        = "prod"
  vpc_id             = module.vpc.vpc_id
  vpc_cidr           = "10.20.0.0/16"
  subnet_ids         = module.vpc.private_subnet_ids
  node_type          = "cache.m5.large"
  num_cache_clusters = 2
}
