variable "cluster_name" {
  description = "Kubernetes Cluster Name"
}

variable "cluster_sg_id" {
  description = "ID of the cluster's security group"
}


variable "public_subnet_ids" {
  description = "List of Public Subnet's ID"
  type        = "list"
}

