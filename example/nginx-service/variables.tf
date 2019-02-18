variable "namespace_name" {
  default = "nginx-service"
  type    = "string"
}

variable "nginx_pod_name" {
  default = "nginx-service"
  type    = "string"
}

variable "nginx_pod_image" {
  default = "nginx:latest"
  type    = "string"
}

variable "cluster_name" {
  default = "EKS Cluster Name"
  type    = "string"
}
