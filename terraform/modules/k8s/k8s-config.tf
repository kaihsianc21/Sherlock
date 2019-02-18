resource "local_file" "eks-config" {
    content     = "${local.kubeconfig}"
    filename = "kubeconfig"
}
resource "null_resource" "kubeconfig" {
  triggers { 
    template = "${local_file.eks-config.content}"
  }

  provisioner "local-exec" {
    command = "cp kubeconfig $HOME/.kube/config"
  }
}


resource "local_file" "config-map-aws-auth" {
    content     = "${local.config-map-aws-auth}"
    filename = "config-map-aws-auth.yaml"
}
resource "null_resource" "aws-auth" {
  depends_on = ["null_resource.kubeconfig"]
  triggers { 
    template = "${local_file.config-map-aws-auth.content}"
  }
  provisioner "local-exec" {
    command = "kubectl apply -f config-map-aws-auth.yaml"
  }
}

