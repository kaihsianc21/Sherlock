variable "cluster_name" {
  description = "Kubernetes Cluster Name"
}

## VPC Variables
variable "vpc_id" {
  description = "ID of the VPC to create subnet"
}

variable "workstation-external-cidr" {
  description = "local workstation's external CIDR"
}