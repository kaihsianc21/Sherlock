provider "external" {
  version = "~> 1.0"
}

data "external" "aws_iam_authenticator" {
  program = ["bash", "${path.module}/authenticator.sh"]

  query {
    cluster_name = "${var.cluster_name}"
  }
}

provider "kubernetes" {
  token = "${data.external.aws_iam_authenticator.result.token}"
  version = "~> 1.1"
}


