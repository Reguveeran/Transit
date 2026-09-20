resource "kubernetes_deployment" "backend" {
  metadata {
    name      = "backend"
    namespace = var.namespace
    labels = {
      app         = "backend"
      environment = var.environment
      managed_by  = "terraform"
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
        app = "backend"
      }
    }

    template {
      metadata {
        labels = {
          app         = "backend"
          environment = var.environment
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
              name = var.config_map_name
            }
          }

          env_from {
            secret_ref {
              name = var.secret_name
            }
          }

          resources {
            requests = {
              cpu    = var.backend_cpu_request
              memory = var.backend_memory_request
            }
            limits = {
              cpu    = var.backend_cpu_limit
              memory = var.backend_memory_limit
            }
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
}

resource "kubernetes_service" "backend_service" {
  metadata {
    name      = "backend-service"
    namespace = var.namespace
    labels = {
      app         = "backend"
      environment = var.environment
      managed_by  = "terraform"
    }
  }

  spec {
    selector = {
      app = "backend"
    }

    port {
      port        = 8000
      target_port = 8000
      name        = "http"
    }
  }
}

resource "kubernetes_deployment" "worker_position" {
  metadata {
    name      = "worker-position"
    namespace = var.namespace
    labels = {
      app         = "worker-position"
      environment = var.environment
      managed_by  = "terraform"
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
          app         = "worker-position"
          environment = var.environment
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
              name = var.config_map_name
            }
          }

          env_from {
            secret_ref {
              name = var.secret_name
            }
          }

          resources {
            requests = {
              cpu    = var.worker_cpu_request
              memory = var.worker_memory_request
            }
            limits = {
              cpu    = var.worker_cpu_limit
              memory = var.worker_memory_limit
            }
          }
        }
      }
    }
  }
}

resource "kubernetes_deployment" "worker_alert" {
  metadata {
    name      = "worker-alert"
    namespace = var.namespace
    labels = {
      app         = "worker-alert"
      environment = var.environment
      managed_by  = "terraform"
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
          app         = "worker-alert"
          environment = var.environment
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
              name = var.config_map_name
            }
          }

          env_from {
            secret_ref {
              name = var.secret_name
            }
          }

          resources {
            requests = {
              cpu    = var.worker_cpu_request
              memory = var.worker_memory_request
            }
            limits = {
              cpu    = var.worker_cpu_limit
              memory = var.worker_memory_limit
            }
          }
        }
      }
    }
  }
}
