# ==============================================================================
# AWS EKS Workloads Module — Stateless UniTransit Microservices Deployment
# ==============================================================================

# 1. Dedicated EKS Namespace
resource "kubernetes_namespace" "unitransit" {
  metadata {
    name = var.namespace
    labels = {
      "app.kubernetes.io/name"       = "unitransit"
      "app.kubernetes.io/managed-by" = "terraform"
      "environment"                  = var.environment
    }
  }
}

# 2. Runtime Decoupled ConfigMap (Injecting AWS RDS / ElastiCache Endpoints)
resource "kubernetes_config_map" "unitransit_config" {
  metadata {
    name      = "unitransit-config"
    namespace = kubernetes_namespace.unitransit.metadata[0].name
    labels = {
      "app.kubernetes.io/part-of" = "unitransit"
      "environment"               = var.environment
    }
  }

  data = {
    DEBUG                      = "0"
    DJANGO_SETTINGS_MODULE     = "config.settings"
    ALLOWED_HOSTS              = "*"
    CORS_ALLOW_ALL_ORIGINS     = "True"
    POSTGRES_HOST              = var.postgres_host
    POSTGRES_PORT              = tostring(var.postgres_port)
    POSTGRES_DB                = var.postgres_db
    POSTGRES_USER              = var.postgres_user
    REDIS_HOST                 = var.redis_host
    REDIS_PORT                 = tostring(var.redis_port)
    REDIS_STREAM_KEY           = var.redis_stream_key
    PROMETHEUS_METRICS_ENABLED = "True"
  }
}

# 3. Secure Runtime Secrets
resource "kubernetes_secret" "unitransit_secrets" {
  metadata {
    name      = "unitransit-secrets"
    namespace = kubernetes_namespace.unitransit.metadata[0].name
    labels = {
      "app.kubernetes.io/part-of" = "unitransit"
      "environment"               = var.environment
    }
  }

  data = {
    POSTGRES_PASSWORD = var.postgres_password
    DJANGO_SECRET_KEY = var.django_secret_key
  }

  type = "Opaque"
}

# 4. Controlled Database Migration & PostGIS Validation Job
resource "kubernetes_job" "db_migrate" {
  metadata {
    name      = "unitransit-db-migrate"
    namespace = kubernetes_namespace.unitransit.metadata[0].name
    labels = {
      "app.kubernetes.io/part-of" = "unitransit"
      "app.kubernetes.io/name"    = "db-migrate"
      "environment"               = var.environment
    }
  }

  spec {
    backoff_limit = 3

    template {
      metadata {
        labels = {
          "app.kubernetes.io/name" = "db-migrate"
          "environment"            = var.environment
        }
      }

      spec {
        restart_policy = "OnFailure"

        container {
          name              = "db-migrate"
          image             = var.backend_image
          image_pull_policy = "IfNotPresent"
          command = [
            "sh",
            "-c",
            "python manage.py migrate --noinput && python -c 'import django; django.setup(); from django.db import connection; cursor = connection.cursor(); cursor.execute(\"SELECT PostGIS_Version();\"); print(\"PostGIS Version:\", cursor.fetchone()[0])'"
          ]

          env_from {
            config_map_ref {
              name = kubernetes_config_map.unitransit_config.metadata[0].name
            }
          }

          env_from {
            secret_ref {
              name = kubernetes_secret.unitransit_secrets.metadata[0].name
            }
          }

          resources {
            requests = {
              cpu    = "100m"
              memory = "128Mi"
            }
            limits = {
              cpu    = "500m"
              memory = "512Mi"
            }
          }
        }
      }
    }
  }
}

# 5. Stateless Backend Deployment (Daphne ASGI Server HTTP + WebSocket)
resource "kubernetes_deployment" "backend" {
  metadata {
    name      = "backend"
    namespace = kubernetes_namespace.unitransit.metadata[0].name
    labels = {
      "app.kubernetes.io/name"    = "backend"
      "app.kubernetes.io/part-of" = "unitransit"
      "environment"               = var.environment
    }
  }

  spec {
    replicas = var.backend_replicas

    strategy {
      type = "RollingUpdate"
      rolling_update {
        max_surge       = "1"
        max_unavailable = "0"
      }
    }

    selector {
      match_labels = {
        "app.kubernetes.io/name" = "backend"
      }
    }

    template {
      metadata {
        labels = {
          "app.kubernetes.io/name"    = "backend"
          "app.kubernetes.io/part-of" = "unitransit"
          "environment"               = var.environment
        }
        annotations = {
          "prometheus.io/scrape" = "true"
          "prometheus.io/port"   = "8000"
          "prometheus.io/path"   = "/metrics"
        }
      }

      spec {
        container {
          name              = "backend"
          image             = var.backend_image
          image_pull_policy = "IfNotPresent"

          port {
            name           = "http"
            container_port = 8000
          }

          env_from {
            config_map_ref {
              name = kubernetes_config_map.unitransit_config.metadata[0].name
            }
          }

          env_from {
            secret_ref {
              name = kubernetes_secret.unitransit_secrets.metadata[0].name
            }
          }

          resources {
            requests = {
              cpu    = var.backend_resources.cpu_request
              memory = var.backend_resources.memory_request
            }
            limits = {
              cpu    = var.backend_resources.cpu_limit
              memory = var.backend_resources.memory_limit
            }
          }

          startup_probe {
            http_get {
              path = "/health"
              port = 8000
            }
            initial_delay_seconds = 10
            period_seconds        = 5
            failure_threshold     = 10
          }

          liveness_probe {
            http_get {
              path = "/health"
              port = 8000
            }
            initial_delay_seconds = 15
            period_seconds        = 10
            timeout_seconds       = 3
          }

          readiness_probe {
            http_get {
              path = "/ready"
              port = 8000
            }
            initial_delay_seconds = 10
            period_seconds        = 5
            timeout_seconds       = 3
          }
        }
      }
    }
  }

  depends_on = [kubernetes_job.db_migrate]
}

# 6. Internal Backend ClusterIP Service
resource "kubernetes_service" "backend_service" {
  metadata {
    name      = "backend-service"
    namespace = kubernetes_namespace.unitransit.metadata[0].name
    labels = {
      "app.kubernetes.io/name"    = "backend"
      "app.kubernetes.io/part-of" = "unitransit"
      "environment"               = var.environment
    }
  }

  spec {
    selector = {
      "app.kubernetes.io/name" = "backend"
    }

    port {
      name        = "http"
      port        = 8000
      target_port = 8000
    }
  }
}

# 7. Stateless PositionWorker Deployment (Redis Stream Consumer Group)
resource "kubernetes_deployment" "worker_position" {
  metadata {
    name      = "worker-position"
    namespace = kubernetes_namespace.unitransit.metadata[0].name
    labels = {
      "app.kubernetes.io/name"    = "worker-position"
      "app.kubernetes.io/part-of" = "unitransit"
      "environment"               = var.environment
    }
  }

  spec {
    replicas = var.position_worker_replicas

    selector {
      match_labels = {
        "app.kubernetes.io/name" = "worker-position"
      }
    }

    template {
      metadata {
        labels = {
          "app.kubernetes.io/name"    = "worker-position"
          "app.kubernetes.io/part-of" = "unitransit"
          "environment"               = var.environment
        }
      }

      spec {
        container {
          name              = "worker-position"
          image             = var.worker_image
          image_pull_policy = "IfNotPresent"
          working_dir       = "/app"
          command           = ["python", "workers/position_worker/position_worker.py"]

          env {
            name  = "PYTHONPATH"
            value = "/app/backend:/app"
          }

          env_from {
            config_map_ref {
              name = kubernetes_config_map.unitransit_config.metadata[0].name
            }
          }

          env_from {
            secret_ref {
              name = kubernetes_secret.unitransit_secrets.metadata[0].name
            }
          }

          resources {
            requests = {
              cpu    = var.worker_resources.cpu_request
              memory = var.worker_resources.memory_request
            }
            limits = {
              cpu    = var.worker_resources.cpu_limit
              memory = var.worker_resources.memory_limit
            }
          }
        }
      }
    }
  }

  depends_on = [kubernetes_job.db_migrate]
}

# 8. Stateless AlertWorker Deployment
resource "kubernetes_deployment" "worker_alert" {
  metadata {
    name      = "worker-alert"
    namespace = kubernetes_namespace.unitransit.metadata[0].name
    labels = {
      "app.kubernetes.io/name"    = "worker-alert"
      "app.kubernetes.io/part-of" = "unitransit"
      "environment"               = var.environment
    }
  }

  spec {
    replicas = var.alert_worker_replicas

    selector {
      match_labels = {
        "app.kubernetes.io/name" = "worker-alert"
      }
    }

    template {
      metadata {
        labels = {
          "app.kubernetes.io/name"    = "worker-alert"
          "app.kubernetes.io/part-of" = "unitransit"
          "environment"               = var.environment
        }
      }

      spec {
        container {
          name              = "worker-alert"
          image             = var.worker_image
          image_pull_policy = "IfNotPresent"
          working_dir       = "/app"
          command           = ["python", "workers/alert_worker/alert_worker.py"]

          env {
            name  = "PYTHONPATH"
            value = "/app/backend:/app"
          }

          env_from {
            config_map_ref {
              name = kubernetes_config_map.unitransit_config.metadata[0].name
            }
          }

          env_from {
            secret_ref {
              name = kubernetes_secret.unitransit_secrets.metadata[0].name
            }
          }

          resources {
            requests = {
              cpu    = var.worker_resources.cpu_request
              memory = var.worker_resources.memory_request
            }
            limits = {
              cpu    = var.worker_resources.cpu_limit
              memory = var.worker_resources.memory_limit
            }
          }
        }
      }
    }
  }

  depends_on = [kubernetes_job.db_migrate]
}

# 9. Stateless Frontend Deployment (React Production Nginx)
resource "kubernetes_deployment" "frontend" {
  metadata {
    name      = "frontend"
    namespace = kubernetes_namespace.unitransit.metadata[0].name
    labels = {
      "app.kubernetes.io/name"    = "frontend"
      "app.kubernetes.io/part-of" = "unitransit"
      "environment"               = var.environment
    }
  }

  spec {
    replicas = var.frontend_replicas

    selector {
      match_labels = {
        "app.kubernetes.io/name" = "frontend"
      }
    }

    template {
      metadata {
        labels = {
          "app.kubernetes.io/name"    = "frontend"
          "app.kubernetes.io/part-of" = "unitransit"
          "environment"               = var.environment
        }
      }

      spec {
        container {
          name              = "frontend"
          image             = var.frontend_image
          image_pull_policy = "IfNotPresent"

          port {
            name           = "http"
            container_port = 80
          }

          resources {
            requests = {
              cpu    = var.frontend_resources.cpu_request
              memory = var.frontend_resources.memory_request
            }
            limits = {
              cpu    = var.frontend_resources.cpu_limit
              memory = var.frontend_resources.memory_limit
            }
          }

          liveness_probe {
            http_get {
              path = "/"
              port = 80
            }
            initial_delay_seconds = 10
            period_seconds        = 10
          }

          readiness_probe {
            http_get {
              path = "/"
              port = 80
            }
            initial_delay_seconds = 5
            period_seconds        = 5
          }
        }
      }
    }
  }
}

# 10. Internal Frontend ClusterIP Service
resource "kubernetes_service" "frontend_service" {
  metadata {
    name      = "frontend-service"
    namespace = kubernetes_namespace.unitransit.metadata[0].name
    labels = {
      "app.kubernetes.io/name"    = "frontend"
      "app.kubernetes.io/part-of" = "unitransit"
      "environment"               = var.environment
    }
  }

  spec {
    selector = {
      "app.kubernetes.io/name" = "frontend"
    }

    port {
      name        = "http"
      port        = 80
      target_port = 80
    }
  }
}
