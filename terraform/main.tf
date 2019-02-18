

module "vpc_network" {
  source       = "./modules/network/vpc/"

  cluster_name = "${var.cluster_name}"
  vpc_cidr_block   = "${var.vpc_cidr_block}"
}

module "igw_network" {
  source       = "./modules/network/igw/"

  cluster_name = "${var.cluster_name}"
  vpc_id       = "${module.vpc_network.vpc_id}"
}

module "security_groups" {
  source       = "./modules/network/security_group/"

  cluster_name = "${var.cluster_name}"
  vpc_id       = "${module.vpc_network.vpc_id}"
  workstation-external-cidr = "${local.workstation-external-cidr}"
}

module "route_table_network" {
  source       = "./modules/network/route_table/"

  cluster_name = "${var.cluster_name}"
  vpc_id       = "${module.vpc_network.vpc_id}"
  igw_id       = "${module.igw_network.igw_id}"
}

module "subnet_network"{
  source       = "./modules/network/subnet/"

  cluster_name = "${var.cluster_name}"
  vpc_cidr_prefix   = "${var.vpc_cidr_prefix}"
  vpc_id            = "${module.vpc_network.vpc_id}"
  public_rt_id      = "${module.route_table_network.public_rt_id}"
}


module "eks_cluster" {
  source                = "./modules/eks-cluster/"

  cluster_name          = "${var.cluster_name}"
  cluster_sg_id         = "${module.security_groups.cluster_sg_id}"
  public_subnet_ids     = "${module.subnet_network.public_subnet_ids}"
}

module "eks_worker_nodes" {
  source                = "./modules/eks-worker-nodes/"

  cluster_name          = "${var.cluster_name}"
  node_sg_id            = "${module.security_groups.node_sg_id}"
  public_subnet_ids     = "${module.subnet_network.public_subnet_ids}"

  node_image_id      = "${var.node_image_id}"
  node_instance_type = "${var.node_instance_type}"

  nodes_desired_capacity      = "${var.nodes_desired_capacity}"
  nodes_max_size              = "${var.nodes_max_size}"
  nodes_min_size              = "${var.nodes_min_size}"
  
  eks_cluster_endpoint        = "${module.eks_cluster.eks_cluster_endpoint}"
  eks_cluster_cert_auth_0data = "${module.eks_cluster.eks_cluster_cert_auth_0data}"
}


module "k8s" {
  source = "./modules/k8s/"

  cluster_name = "${var.cluster_name}"
  eks_node_arn = "${module.eks_worker_nodes.node_arn}"
  eks_cluster_endpoint        = "${module.eks_cluster.eks_cluster_endpoint}"
  eks_cluster_cert_auth_0data = "${module.eks_cluster.eks_cluster_cert_auth_0data}" 

  namespace             = "${var.namespace}"
  api_port              = "${var.api_port}"
  api_replicas          = "${var.api_replicas}"
  AWS_ACCESS_KEY_ID     = "${var.AWS_ACCESS_KEY_ID}"
  AWS_SECRET_ACCESS_KEY = "${var.AWS_SECRET_ACCESS_KEY}"
}

