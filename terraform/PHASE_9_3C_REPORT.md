# UniTransit Phase 9.3C: AWS Managed Data Tier Report

**Phase Status**: **COMPLETED & VALIDATED**  
**Date**: September 20, 2026  
**Scope**: AWS RDS PostgreSQL with PostGIS, AWS ElastiCache Redis Replication Group, Application Configuration Abstraction  
**Target Modules**: `terraform/aws/modules/{rds,elasticache}`  
**Target Environments**: `terraform/aws/environments/{dev,prod}`  

---

## 1. Executive Summary

Phase 9.3C models the AWS Managed Data Tier and configuration abstraction for UniTransit:
1. **Managed Stateful Layer**: Modeled Multi-AZ AWS RDS PostgreSQL (PostGIS) and AWS ElastiCache Redis replication groups within private database subnets.
2. **Strict Micro-Segmentation**: Database and Cache tiers accept traffic strictly on ports 5432 and 6379 from the EKS Worker Node Security Group; direct internet access is completely blocked.
3. **Application Decoupling**: Containers remain environment-agnostic; identical Docker images run locally and in AWS by swapping environment variable bindings injected via ConfigMaps and Secrets.
4. **PostGIS & Stream Compatibility**: Validated spatial models (`Stop`, `Route`, `VehiclePosition`) and Redis Stream ingestion pipelines against PostgreSQL/Redis contracts.
5. **Zero Impact on Local Environments**: Local clusters (`unitransit-dev` 8/8, `unitransit-iac` 8/8, `unitransit` 6/6) and the regression suite (77/77 tests) remain active and healthy.

---

## 2. Module Specifications

### A. RDS PostgreSQL Module (`terraform/aws/modules/rds/`)
- **Engine**: PostgreSQL 15.7 with PostGIS extension support
- **Parameter Group**: Custom parameter group forcing SSL (`rds.force_ssl = 1`) and `pg_stat_statements`
- **Security & Encryption**: KMS storage encryption (`storage_encrypted = true`), private DB subnet group
- **High Availability**: Multi-AZ failover enabled for production (`db.r6g.large`, 100 GiB), single-AZ for dev (`db.t4g.medium`, 20 GiB)
- **Backup Policy**: 7-day retention in dev, 30-day retention in prod with deletion protection

### B. ElastiCache Redis Module (`terraform/aws/modules/elasticache/`)
- **Engine**: Redis 7.1 with Redis Streams support (`transport.events`)
- **Parameter Group**: `maxmemory-policy = noeviction` (protects stream event backlog from data loss)
- **Security & Encryption**: In-transit TLS encryption and at-rest KMS encryption
- **High Availability**: Automatic failover and Multi-AZ replication group with 3 nodes in prod (`cache.r6g.large`), single node in dev (`cache.t4g.small`)

---

## 3. Application Configuration Mapping

| Component | Variable | Local Kubernetes Value | AWS Cloud Value (Injected at Runtime) |
| :--- | :--- | :--- | :--- |
| **Database Host** | `POSTGRES_HOST` | `postgres-service` | `module.rds.db_address` |
| **Database Port** | `POSTGRES_PORT` | `5432` | `module.rds.db_port` |
| **Database Name** | `POSTGRES_DB` | `unitransit` | `module.rds.db_name` |
| **Database User** | `POSTGRES_USER` | `unitransit` | `module.rds.db_username` |
| **Redis Host** | `REDIS_HOST` | `redis-service` | `module.elasticache.primary_endpoint_address` |
| **Redis Port** | `REDIS_PORT` | `6379` | `module.elasticache.port` |
| **Redis Stream** | `REDIS_STREAM_KEY` | `transport.events` | `transport.events` |

---

## 4. Protected Environments & Regression Status

- `unitransit` namespace: **Untouched & Active (6/6 pods running)**
- `unitransit-iac` namespace: **Untouched & Active (8/8 pods running)**
- `unitransit-dev` namespace: **Untouched & Active (8/8 pods running)**
- Full regression baseline: **77/77 tests passing (Ran 77 tests in 30.394s, OK)**

---

## 5. Next Recommended Step

Proceed to **Phase 9.3D: Deploy UniTransit Workloads to EKS & Load Balancer Ingress**.
