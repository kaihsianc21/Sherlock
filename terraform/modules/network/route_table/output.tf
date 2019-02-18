output "public_rt_id" {
  description = "The ID of the Public Route Table"
  value       = "${aws_route_table.public-rt.id}"
}