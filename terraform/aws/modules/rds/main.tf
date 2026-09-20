# ==============================================================================
# AWS RDS Module — Multi-AZ PostgreSQL with PostGIS for Spatial Persistence
# ==============================================================================

resource "aws_db_parameter_group" "rds" {
  name        = "unitransit-pg15-params-${var.environment}"
  family      = "postgres15"
  description = "Custom parameter group for UniTransit PostgreSQL 15 PostGIS database"

  parameter {
    name  = "rds.force_ssl"
    value = "1"
  }

  parameter {
    name  = "shared_preload_libraries"
    value = "pg_stat_statements"
  }

  tags = {
    Name        = "unitransit-pg-params-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_db_instance" "main" {
  identifier                  = "unitransit-db-${var.environment}"
  engine                      = "postgres"
  engine_version              = var.engine_version
  instance_class              = var.instance_class
  allocated_storage           = var.allocated_storage
  max_allocated_storage       = var.max_allocated_storage
  storage_type                = "gp3"
  storage_encrypted           = true
  multi_az                    = var.multi_az
  publicly_accessible         = false
  auto_minor_version_upgrade  = true
  allow_major_version_upgrade = false

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password
  port     = 5432

  db_subnet_group_name   = var.db_subnet_group_name
  vpc_security_group_ids = [var.security_group_id]
  parameter_group_name   = aws_db_parameter_group.rds.name

  backup_retention_period   = var.backup_retention_period
  backup_window             = "03:00-04:00"
  maintenance_window        = "Mon:04:30-Mon:05:30"
  copy_tags_to_snapshot     = true
  deletion_protection       = var.deletion_protection
  skip_final_snapshot       = var.environment != "prod"
  final_snapshot_identifier = var.environment == "prod" ? "unitransit-db-final-snapshot-${var.environment}" : null

  tags = {
    Name        = "unitransit-db-${var.environment}"
    Environment = var.environment
    Engine      = "PostgreSQL-PostGIS"
  }
}
