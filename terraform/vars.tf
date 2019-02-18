#
# Variables Configuration
#

variable "cluster_name" {
  default = "sherlock-eks"
  type    = "string"
}

variable "vpc_cidr_block" {
  default = "10.0.0.0/16"
}

variable "vpc_cidr_prefix" {
  default = "10.0"
}

variable "node_image_id" {
  default = "ami-081099ec932b99961"
}

variable "node_instance_type" {
  default = "m4.xlarge"
}

variable "nodes_desired_capacity" {
  default = 2
}

variable "nodes_max_size" {
  default = 5
}

variable "nodes_min_size" {
  default = 1
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



