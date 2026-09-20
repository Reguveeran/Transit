# ==============================================================================
# AWS Ingress Module — Application Load Balancer Ingress Resource
# ==============================================================================

locals {
  annotations = merge(
    {
      "kubernetes.io/ingress.class"                            = "alb"
      "alb.ingress.kubernetes.io/scheme"                       = "internet-facing"
      "alb.ingress.kubernetes.io/target-type"                  = "ip"
      "alb.ingress.kubernetes.io/subnets"                      = join(",", var.public_subnet_ids)
      "alb.ingress.kubernetes.io/security-groups"              = var.alb_security_group_id
      "alb.ingress.kubernetes.io/load-balancer-name"           = "unitransit-alb-${var.environment}"
      "alb.ingress.kubernetes.io/load-balancer-attributes"     = "idle_timeout.timeout_seconds=300"
      "alb.ingress.kubernetes.io/healthcheck-path"             = "/health"
      "alb.ingress.kubernetes.io/healthcheck-interval-seconds" = "15"
      "alb.ingress.kubernetes.io/healthcheck-timeout-seconds"  = "5"
      "alb.ingress.kubernetes.io/healthy-threshold-count"      = "2"
      "alb.ingress.kubernetes.io/unhealthy-threshold-count"    = "3"
    },
    var.enable_tls && var.certificate_arn != "" ? {
      "alb.ingress.kubernetes.io/listen-ports"    = "[{\"HTTP\": 80}, {\"HTTPS\": 443}]"
      "alb.ingress.kubernetes.io/ssl-redirect"    = "443"
      "alb.ingress.kubernetes.io/certificate-arn" = var.certificate_arn
      "alb.ingress.kubernetes.io/ssl-policy"      = "ELBSecurityPolicy-TLS13-1-2-2021-06"
      } : {
      "alb.ingress.kubernetes.io/listen-ports" = "[{\"HTTP\": 80}]"
    }
  )
}

resource "kubernetes_ingress_v1" "unitransit" {
  metadata {
    name        = "unitransit-ingress"
    namespace   = var.namespace
    annotations = local.annotations
    labels = {
      "app.kubernetes.io/name"       = "unitransit-ingress"
      "app.kubernetes.io/managed-by" = "terraform"
      "environment"                  = var.environment
    }
  }

  spec {
    ingress_class_name = "alb"

    rule {
      host = var.domain_name != "" ? var.domain_name : null

      http {
        # 1. Real-time WebSocket Ingestion / Telemetry Channel
        path {
          path      = "/ws"
          path_type = "Prefix"

          backend {
            service {
              name = var.backend_service_name
              port {
                number = var.backend_service_port
              }
            }
          }
        }

        # 2. REST API Endpoints
        path {
          path      = "/api"
          path_type = "Prefix"

          backend {
            service {
              name = var.backend_service_name
              port {
                number = var.backend_service_port
              }
            }
          }
        }

        # 3. Static/Frontend Web Tier
        path {
          path      = "/static"
          path_type = "Prefix"

          backend {
            service {
              name = var.backend_service_name
              port {
                number = var.backend_service_port
              }
            }
          }
        }

        # 4. Root / Single Page Application
        path {
          path      = "/"
          path_type = "Prefix"

          backend {
            service {
              name = var.frontend_service_name
              port {
                number = var.frontend_service_port
              }
            }
          }
        }
      }
    }
  }
}
