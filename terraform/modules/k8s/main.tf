#
# * Sherlock Deployment
# * Install k8s-nvidia-device-plugin
# * Create Namespace
# * Create API Sets
# * Create Redis
# * Create Tensorflow Services
# 

resource "null_resource" "k8s-nvidia-plugin" {
  depends_on = ["null_resource.aws-auth"]

  provisioner "local-exec" {
    command = "kubectl apply -f '${path.root}/modules/sherlock/nvidia-device-plugin.yml'"
  }
}


resource "null_resource" "namespace" {
  depends_on = ["null_resource.aws-auth"]

  provisioner "local-exec" {
    command = <<EOF
    echo '${data.template_file.namespace.rendered}' > /tmp/namespace.yaml &&
    kubectl apply -f /tmp/namespace.yaml
  EOF
  }

  provisioner "local-exec" {
    when = "destroy"
    command = <<EOF
    echo '${data.template_file.namespace.rendered}' > /tmp/namespace.yaml &&
    kubectl delete -f /tmp/namespace.yaml
  EOF
  }
}

resource "null_resource" "api-deployment" {
  depends_on = ["null_resource.namespace"]

  provisioner "local-exec" {
    command = <<EOF
    echo '${data.template_file.api-deployment.rendered}' > /tmp/api.yaml &&
    kubectl apply -f /tmp/api.yaml
  EOF
  }
}

resource "null_resource" "redis-deployment" {
  depends_on = ["null_resource.namespace"]

  provisioner "local-exec" {
    command = <<EOF
    echo '${data.template_file.redis-deployment.rendered}' > /tmp/redis.yaml &&
    kubectl apply -f /tmp/redis.yaml
  EOF
  }
}

resource "null_resource" "tf-deployment" {
  depends_on = ["null_resource.namespace"]

  provisioner "local-exec" {
    command = <<EOF
    echo '${data.template_file.tf-deployment.rendered}' > /tmp/tf.yaml &&
    kubectl apply -f /tmp/tf.yaml
  EOF
  }
}
