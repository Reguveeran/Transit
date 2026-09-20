resource "kubernetes_namespace" "unitransit_iac" {
  metadata {
    name = var.namespace
    labels = {
      environment = "iac"
      managed_by  = "terraform"
      app         = "unitransit"
    }
  }
}
