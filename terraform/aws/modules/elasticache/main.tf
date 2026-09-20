# ==============================================================================
# AWS ElastiCache Module — Multi-AZ Redis Replication Group for Streams & Pub/Sub
# ==============================================================================

# 1. ElastiCache Subnet Group (Private Database Subnets)
resource "aws_elasticache_subnet_group" "redis" {
  name        = "unitransit-redis-subnet-group-${var.environment}"
  description = "Subnet group for UniTransit ElastiCache Redis replication group"
  subnet_ids  = var.subnet_ids

  tags = {
    Name        = "unitransit-redis-subnet-group-${var.environment}"
    Environment = var.environment
  }
}

# 2. ElastiCache Redis Parameter Group
resource "aws_elasticache_parameter_group" "redis" {
  name        = "unitransit-redis7-params-${var.environment}"
  family      = "redis7"
  description = "Custom parameter group for UniTransit Redis 7.1 stream broker"

  parameter {
    name  = "maxmemory-policy"
    value = "noeviction" # Protect stream events from volatile eviction
  }

  tags = {
    Name        = "unitransit-redis-params-${var.environment}"
    Environment = var.environment
  }
}

# 3. ElastiCache Redis Replication Group
resource "aws_elasticache_replication_group" "main" {
  replication_group_id = "unitransit-redis-${var.environment}"
  description          = "Redis streaming message broker for UniTransit telemetry ingestion"

  engine         = "redis"
  engine_version = var.engine_version
  node_type      = var.node_type
  port           = var.port

  num_cache_clusters         = var.num_cache_clusters
  automatic_failover_enabled = var.automatic_failover_enabled
  multi_az_enabled           = var.multi_az_enabled

  subnet_group_name    = aws_elasticache_subnet_group.redis.name
  security_group_ids   = [var.security_group_id]
  parameter_group_name = aws_elasticache_parameter_group.redis.name

  transit_encryption_enabled = var.transit_encryption_enabled
  at_rest_encryption_enabled = var.at_rest_encryption_enabled

  maintenance_window       = "sun:05:00-sun:06:00"
  snapshot_window          = "03:00-04:00"
  snapshot_retention_limit = var.environment == "prod" ? 7 : 0

  auto_minor_version_upgrade = true
  apply_immediately          = var.environment != "prod"

  tags = {
    Name        = "unitransit-redis-${var.environment}"
    Environment = var.environment
    Component   = "StreamBroker"
  }
}
