resource "kubernetes_config_map" "unitransit_config" {
  metadata {
    name      = "unitransit-config"
    namespace = kubernetes_namespace.unitransit_iac.metadata[0].name
    labels = {
      app        = "unitransit"
      managed_by = "terraform"
    }
  }

  data = {
    DEBUG                         = "False"
    ALLOWED_HOSTS                 = "*"
    PYTHONPATH                    = "/app:/app/backend"
    POSTGRES_DB                   = var.postgres_db
    POSTGRES_HOST                 = "postgres-service"
    POSTGRES_PORT                 = "5432"
    REDIS_HOST                    = "redis-service"
    REDIS_PORT                    = "6379"
    REDIS_STREAM_KEY              = "transport.events"
    REDIS_GROUP_NAME              = "unitransit_workers"
    SIMULATOR_VEHICLES_COUNT      = "50"
    SIMULATOR_UPDATE_INTERVAL_SEC = "2.0"
    SIMULATOR_FAULT_RATE          = "0.02"
  }
}

resource "kubernetes_secret" "unitransit_secrets" {
  metadata {
    name      = "unitransit-secrets"
    namespace = kubernetes_namespace.unitransit_iac.metadata[0].name
    labels = {
      app        = "unitransit"
      managed_by = "terraform"
    }
  }

  type = "Opaque"

  data = {
    SECRET_KEY        = var.secret_key
    POSTGRES_USER     = var.postgres_user
    POSTGRES_PASSWORD = var.postgres_password
  }
}
