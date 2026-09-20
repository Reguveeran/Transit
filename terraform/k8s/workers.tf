resource "kubernetes_deployment" "worker_position" {
  metadata {
    name      = "worker-position"
    namespace = kubernetes_namespace.unitransit_iac.metadata[0].name
    labels = {
      app        = "worker-position"
      managed_by = "terraform"
    }
  }

  spec {
    replicas = var.position_worker_replicas

    selector {
      match_labels = {
        app = "worker-position"
      }
    }

    template {
      metadata {
        labels = {
          app = "worker-position"
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
              cpu    = "150m"
              memory = "256Mi"
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

  depends_on = [
    kubernetes_deployment.redis,
    kubernetes_stateful_set.postgres,
  ]
}

resource "kubernetes_deployment" "worker_alert" {
  metadata {
    name      = "worker-alert"
    namespace = kubernetes_namespace.unitransit_iac.metadata[0].name
    labels = {
      app        = "worker-alert"
      managed_by = "terraform"
    }
  }

  spec {
    replicas = var.alert_worker_replicas

    selector {
      match_labels = {
        app = "worker-alert"
      }
    }

    template {
      metadata {
        labels = {
          app = "worker-alert"
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
              cpu    = "150m"
              memory = "256Mi"
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

  depends_on = [
    kubernetes_deployment.redis,
    kubernetes_stateful_set.postgres,
  ]
}
