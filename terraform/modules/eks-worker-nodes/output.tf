

output "node_launch_config_id" {
  description = "The ID of the worker launch configuration"
  value       = "${aws_launch_configuration.nodes.id}"
}

output "node_arn" {
  description = "ARN of Node AWS IAM Role"
  value       = "${aws_iam_role.node.arn}"
}


