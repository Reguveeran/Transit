resource "aws_elasticache_subnet_group" "main" {
  name       = "${var.environment}-unitransit-redis-subnet-group"
  subnet_ids = var.subnet_ids
}

resource "aws_security_group" "redis" {
  name        = "${var.environment}-unitransit-redis-sg"
  description = "Allow inbound redis traffic from VPC"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_elasticache_replication_group" "main" {
  replication_group_id       = "${var.environment}-unitransit-redis"
  description                = "UniTransit real-time event broker redis cluster"
  node_type                  = var.node_type
  num_cache_clusters         = var.num_cache_clusters
  port                       = 6379
  parameter_group_name       = "default.redis7"
  subnet_group_name          = aws_elasticache_subnet_group.main.name
  security_group_ids         = [aws_security_group.redis.id]
  auto_minor_version_upgrade = true
  apply_immediately          = true

  tags = {
    Name        = "${var.environment}-unitransit-redis"
    Environment = var.environment
  }
}
