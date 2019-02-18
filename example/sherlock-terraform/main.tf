
resource "kubernetes_namespace" "sherlock" {
  metadata {
    name = "${var.namespace_name}"
    labels {
      name = "sherlock"
    }
  }
}

resource "kubernetes_deployment" "sherlock-redis-deployment" {
  metadata {
    name = "sherlock-redis-deployment"
    namespace = "${var.namespace_name}"
    labels {
      app = "sherlock-redis"
    }
  }
  spec {
    replicas = 1
    selector {
      match_labels {
        app = "sherlock-redis"
      }
    }
    template {
      metadata {
        labels {
          app = "sherlock-redis"
        }
      }
      spec {
        container {
          image = "redis:latest"
          name  = "sherlock-redis"
        }
      }
    }
  }
}

resource "kubernetes_service" "sherlock-redis-service" {
  metadata {
    name      = "sherlock-redis-service"
    namespace = "${var.namespace_name}"
  }
  spec {
    selector {
      app = "sherlock-redis"
    }
    port {
      port = 6379
      target_port = 6379
    }
    type = "ClusterIP"
  }
}

resource "kubernetes_deployment" "sherlock-tensorflow-deployment" {
  metadata {
    name = "sherlock-tensorflow-deployment"
    namespace = "${var.namespace_name}"
    labels {
      app = "sherlock-tensorflow"
    }
  }
  spec {
    replicas = 2
    selector {
      match_labels {
        app = "sherlock-tensorflow"
      }
    }

    template {
      metadata {
        labels {
          app = "sherlock-tensorflow"
        }
      }

      spec {
        container {
          image             = "kaihsianc/sherlock-tensorflow"
          image_pull_policy = "Always"
          name              = "sherlock-tensorflow"
          # resources {
          #   limits {
          #     "nvidia.com/gpu" = 1
          #   }
          # }
          env {
            name  = "CELERY_BROKER_URL"
            value = "redis://${kubernetes_service.sherlock-redis-service.load_balancer_ingress.0.hostname}:6379/0"
          }
          env {
            name  = "CELERY_RESULT_BACKEND"
            value = "redis://${kubernetes_service.sherlock-redis-service.load_balancer_ingress.0.hostname}:6379/0"
          }
          env {
            name  = "AWS_ACCESS_KEY_ID"
            value = "${AWS_ACCESS_KEY_ID}"
          }
          env {
            name  = "AWS_SECRET_ACCESS_KEY"
            value = "${AWS_SECRET_ACCESS_KEY}"
          }
        }
      }
    }
  }
}

resource "kubernetes_deployment" "sherlock-api-deployment" {
  metadata {
    name = "sherlock-api-deployment"
    namespace = "sherlock"
    labels {
      app = "sherlock-api"
    }
  }
  spec {
    replicas = 3
    selector {
      match_labels {
        app = "sherlock-api"
      }
    }
    template {
      metadata {
        labels {
          app = "sherlock-api"
        }
      }
      spec {
        container {
          image = "kaihsianc/sherlock-api"
          name  = "sherlock-api"
          env {
            name  = "CELERY_BROKER_URL"
            value = "redis://${kubernetes_service.sherlock-redis-service.load_balancer_ingress.0.hostname}:6379/0"
          }
          env {
            name  = "CELERY_RESULT_BACKEND"
            value = "redis://${kubernetes_service.sherlock-redis-service.load_balancer_ingress.0.hostname}:6379/0"
          }
          env {
            name  = "C_FORCE_ROOT"
            value = true
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "sherlock-api-service" {
  metadata {
    name      = "sherlock-api-service"
    namespace = "${var.namespace_name}"
  }
  spec {
    selector {
      app = "sherlock-api"
    }
    port {
      port = 8080
      target_port = 5000
    }
    type = "LoadBalancer"
  }
}