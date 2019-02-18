data "template_file" "namespace" {
  template = "${file("${path.root}/modules/sherlock/sherlock-namespace.yaml")}"
  vars {
    namespace = "${var.namespace}"
  }
}

data "template_file" "api-deployment" {
  template = "${file("${path.root}/modules/sherlock/sherlock-api.yaml")}"
  vars {
    namespace     = "${var.namespace}"
    api_port      = "${var.api_port}"
    api_replicas  = "${var.api_replicas}"
    
  }
}

data "template_file" "redis-deployment" {
  template = "${file("${path.root}/modules/sherlock/sherlock-redis.yaml")}"
  vars {
    namespace = "${var.namespace}"
  }
}

data "template_file" "tf-deployment" {
  template = "${file("${path.root}/modules/sherlock/sherlock-tensorflow.yaml")}"
  vars {
    namespace = "${var.namespace}"
    AWS_ACCESS_KEY_ID     = "${var.AWS_ACCESS_KEY_ID}"
    AWS_SECRET_ACCESS_KEY = "${var.AWS_SECRET_ACCESS_KEY}"
  }
}
