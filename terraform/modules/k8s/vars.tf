variable "cluster_name" {
  description = "Kubernetes Cluster Name"
}

variable "eks_node_arn" {
  description = "ARN for Kubernetes' Nodes"
}

variable "eks_cluster_endpoint" {
  description = "Endpoint of EKS Cluster"
}

variable "eks_cluster_cert_auth_0data" {
  description = "AWS auth of EKS Cluster" 
}

variable "namespace" {
  description = "Namespace of Project on Kubernetes"
}

variable "api_port" {
  description = "Port Exposed for API"
  default = 8080
}

variable "api_replicas" {
  description = "Number of APIs' Replicas"
  default = 2
}

variable "AWS_ACCESS_KEY_ID" {
  description = "AWS Access Key ID"
}

variable "AWS_SECRET_ACCESS_KEY" {
  description = "AWS Secret Access Key"
}




