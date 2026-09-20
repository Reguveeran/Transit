resource "kubernetes_config_map" "prometheus_config" {
  metadata {
    name      = "prometheus-config"
    namespace = var.namespace
    labels = {
      app         = "prometheus"
      environment = var.environment
      managed_by  = "terraform"
    }
  }

  data = {
    "prometheus.yml" = <<-EOT
      global:
        scrape_interval: 5s
        evaluation_interval: 5s

      scrape_configs:
        - job_name: 'unitransit-backend'
          metrics_path: '/metrics'
          static_configs:
            - targets: ['${var.backend_service_name}:${var.backend_service_port}']
    EOT
  }
}

resource "kubernetes_deployment" "prometheus" {
  metadata {
    name      = "prometheus"
    namespace = var.namespace
    labels = {
      app         = "prometheus"
      environment = var.environment
      managed_by  = "terraform"
    }
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "prometheus"
      }
    }

    template {
      metadata {
        labels = {
          app         = "prometheus"
          environment = var.environment
        }
      }

      spec {
        container {
          name              = "prometheus"
          image             = var.prometheus_image
          image_pull_policy = "IfNotPresent"

          port {
            name           = "http"
            container_port = 9090
          }

          volume_mount {
            name       = "config-volume"
            mount_path = "/etc/prometheus/prometheus.yml"
            sub_path   = "prometheus.yml"
          }

          resources {
            requests = {
              cpu    = var.cpu_request
              memory = var.memory_request
            }
            limits = {
              cpu    = "500m"
              memory = "512Mi"
            }
          }
        }

        volume {
          name = "config-volume"
          config_map {
            name = kubernetes_config_map.prometheus_config.metadata[0].name
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "prometheus_service" {
  metadata {
    name      = "prometheus-service"
    namespace = var.namespace
    labels = {
      app         = "prometheus"
      environment = var.environment
      managed_by  = "terraform"
    }
  }

  spec {
    selector = {
      app = "prometheus"
    }

    port {
      port        = 9090
      target_port = 9090
      name        = "http"
    }
  }
}

resource "kubernetes_deployment" "grafana" {
  metadata {
    name      = "grafana"
    namespace = var.namespace
    labels = {
      app         = "grafana"
      environment = var.environment
      managed_by  = "terraform"
    }
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "grafana"
      }
    }

    template {
      metadata {
        labels = {
          app         = "grafana"
          environment = var.environment
        }
      }

      spec {
        container {
          name              = "grafana"
          image             = var.grafana_image
          image_pull_policy = "IfNotPresent"

          port {
            name           = "http"
            container_port = 3000
          }

          env {
            name  = "GF_SECURITY_ADMIN_PASSWORD"
            value = "admin"
          }

          resources {
            requests = {
              cpu    = var.cpu_request
              memory = var.memory_request
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

resource "kubernetes_service" "grafana_service" {
  metadata {
    name      = "grafana-service"
    namespace = var.namespace
    labels = {
      app         = "grafana"
      environment = var.environment
      managed_by  = "terraform"
    }
  }

  spec {
    selector = {
      app = "grafana"
    }

    port {
      port        = 3000
      target_port = 3000
      name        = "http"
    }
  }
}
