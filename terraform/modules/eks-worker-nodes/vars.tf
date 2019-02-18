variable "cluster_name" {
  description = "Kubernetes Cluster Name"
}

#
# Node Network
#

variable "node_sg_id" {
  description = "ID of the Node's Security Group"
}

variable "public_subnet_ids" {
    description = "ID of the Cluster's Public Subnet"
    type = "list"
}

#
# Nodes Launch Configuration
#

variable "node_image_id" {
  description = "ID of Image"
  default     = "ami-081099ec932b99961"
}

variable "node_instance_type" {
  description = "Type of Instance"
  default     = "m4.xlarge"
}


#
# AutoScaling Group
#

variable "nodes_desired_capacity" {
  description = "Desired Node Capacity"
}

variable "nodes_max_size" {
    description = "Maximum Size of Nodes"
}

variable "nodes_min_size" {
  description = "Minimum Size of Nodes"
}


# Node CoreDNS setup

variable "eks_cluster_endpoint" {
  description = "Endpoint of Cluster"
}

variable "eks_cluster_cert_auth_0data" {

}
