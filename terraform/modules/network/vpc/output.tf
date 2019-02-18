output "vpc_id" {
  description = "The ID of the VPC"
  value       = "${aws_vpc.vpc.id}"
}

output "cidr_block" {
  description = ""
  value       = "${aws_vpc.vpc.cidr_block}"
}