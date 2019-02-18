variable "cluster_name" {
  description = "Kubernetes Cluster Name"
}

## VPC Variables
variable "vpc_id" {
  description = "ID of the VPC to create subnet"
}

variable "vpc_cidr_prefix" {
  description = "First 2 section of the VPC Cidr to create "
}

## Route Table
variable "public_rt_id" {
  description = "ID of the Public Route Table"
}