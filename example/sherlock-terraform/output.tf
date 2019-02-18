output "lb_ip" {
  value = "${kubernetes_service.sherlock-api-service.load_balancer_ingress.0.hostname}"
}


output "redis_ip" {
  value = "${kubernetes_service.sherlock-redis-service.load_balancer_ingress.0.hostname}"
}