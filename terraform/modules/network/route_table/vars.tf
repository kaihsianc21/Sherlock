variable "cluster_name" {
  description = "Kubernetes Cluster Name"
}

## VPC Variables
variable "vpc_id" {
  description = "ID of the VPC to create subnet"
}

variable "igw_id" {
  description = "ID of your Internet Gateway"
}
