resource "kubernetes_namespace" "env_namespace" {
  metadata {
    name = var.namespace
    labels = {
      environment = var.environment
      managed_by  = "terraform"
      app         = var.app_name
    }
  }
}

resource "kubernetes_config_map" "unitransit_config" {
  metadata {
    name      = "unitransit-config"
    namespace = kubernetes_namespace.env_namespace.metadata[0].name
    labels = {
      environment = var.environment
      managed_by  = "terraform"
      app         = var.app_name
    }
  }

  data = {
    DEBUG                         = var.debug
    ALLOWED_HOSTS                 = var.allowed_hosts
    PYTHONPATH                    = "/app:/app/backend"
    POSTGRES_DB                   = var.postgres_db
    POSTGRES_HOST                 = var.postgres_host
    POSTGRES_PORT                 = tostring(var.postgres_port)
    REDIS_HOST                    = var.redis_host
    REDIS_PORT                    = tostring(var.redis_port)
    REDIS_STREAM_KEY              = var.redis_stream_key
    REDIS_GROUP_NAME              = var.redis_group_name
    SIMULATOR_VEHICLES_COUNT      = "50"
    SIMULATOR_UPDATE_INTERVAL_SEC = "2.0"
    SIMULATOR_FAULT_RATE          = "0.02"
  }
}

resource "kubernetes_secret" "unitransit_secrets" {
  metadata {
    name      = "unitransit-secrets"
    namespace = kubernetes_namespace.env_namespace.metadata[0].name
    labels = {
      environment = var.environment
      managed_by  = "terraform"
      app         = var.app_name
    }
  }

  type = "Opaque"

  data = {
    SECRET_KEY        = var.secret_key
    POSTGRES_USER     = var.postgres_user
    POSTGRES_PASSWORD = var.postgres_password
  }
}
