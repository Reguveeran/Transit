# ==============================================================================
# AWS Security Groups Module — Least-Privilege Micro-Segmentation for UniTransit
# ==============================================================================

# 1. Application Load Balancer Security Group (Public Ingress)
resource "aws_security_group" "alb" {
  name        = "unitransit-alb-sg-${var.environment}"
  description = "Security group for public Application Load Balancer"
  vpc_id      = var.vpc_id

  ingress {
    description = "HTTP Inbound"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS Inbound"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow all outbound traffic to worker nodes"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "unitransit-alb-sg-${var.environment}"
    Environment = var.environment
  }
}

# 2. EKS Control Plane Security Group
resource "aws_security_group" "eks_cluster" {
  name        = "unitransit-eks-cluster-sg-${var.environment}"
  description = "Security group for EKS control plane communication"
  vpc_id      = var.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name                                        = "unitransit-eks-cluster-sg-${var.environment}"
    Environment                                 = var.environment
    "kubernetes.io/cluster/${var.cluster_name}" = "owned"
  }
}

# 3. EKS Worker Nodes Security Group
resource "aws_security_group" "eks_nodes" {
  name        = "unitransit-eks-nodes-sg-${var.environment}"
  description = "Security group for all EKS worker nodes in node groups"
  vpc_id      = var.vpc_id

  # Allow all node-to-node internal communication
  ingress {
    description = "Allow node-to-node internal communication"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    self        = true
  }

  # Allow traffic from EKS control plane
  ingress {
    description     = "Allow control plane to worker nodes"
    from_port       = 1025
    to_port         = 65535
    protocol        = "tcp"
    security_groups = [aws_security_group.eks_cluster.id]
  }

  # Allow traffic from Application Load Balancer
  ingress {
    description     = "Allow traffic from ALB to worker node NodePorts / Pods"
    from_port       = 0
    to_port         = 65535
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name                                        = "unitransit-eks-nodes-sg-${var.environment}"
    Environment                                 = var.environment
    "kubernetes.io/cluster/${var.cluster_name}" = "owned"
  }
}

# Allow worker nodes to communicate with control plane (Port 443)
resource "aws_security_group_rule" "cluster_inbound_nodes" {
  type                     = "ingress"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.eks_nodes.id
  security_group_id        = aws_security_group.eks_cluster.id
  description              = "Allow worker nodes to communicate with EKS control plane"
}

# 4. RDS PostgreSQL Security Group (Strict Inbound from EKS Nodes Only)
resource "aws_security_group" "rds" {
  name        = "unitransit-rds-sg-${var.environment}"
  description = "Security group for RDS PostgreSQL with PostGIS"
  vpc_id      = var.vpc_id

  ingress {
    description     = "PostgreSQL port 5432 strictly from EKS worker nodes"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.eks_nodes.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "unitransit-rds-sg-${var.environment}"
    Environment = var.environment
  }
}

# 5. ElastiCache Redis Security Group (Strict Inbound from EKS Nodes Only)
resource "aws_security_group" "elasticache" {
  name        = "unitransit-redis-sg-${var.environment}"
  description = "Security group for ElastiCache Redis streaming broker"
  vpc_id      = var.vpc_id

  ingress {
    description     = "Redis port 6379 strictly from EKS worker nodes"
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.eks_nodes.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "unitransit-redis-sg-${var.environment}"
    Environment = var.environment
  }
}
