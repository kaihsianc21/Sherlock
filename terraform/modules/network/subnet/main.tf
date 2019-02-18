#
# Cluster Subnet Resources
#
data "aws_availability_zones" "available" {}

resource "aws_subnet" "public-subnet" {
  count = 2

  vpc_id            = "${var.vpc_id}"
  cidr_block        = "${var.vpc_cidr_prefix}.${count.index}.0/24"
  availability_zone = "${data.aws_availability_zones.available.names[count.index]}"
  
  tags {
      Name = "${var.cluster_name}-public-subnet",
      "kubernetes.io/cluster/${var.cluster_name}" = "shared"
  }
}


resource "aws_route_table_association" "public" {
  count = 2

  subnet_id      = "${aws_subnet.public-subnet.*.id[count.index]}"
  route_table_id = "${var.public_rt_id}"
}
