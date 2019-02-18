#! /bin/bash

#
# Reference:
# https://docs.aws.amazon.com/eks/latest/userguide/dashboard-tutorial.html
#

#
# Step 1. Deploy the Dashboard
#


# Deploy the Kubernetes dashboard to your cluster
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v1.10.1/src/deploy/recommended/kubernetes-dashboard.yaml

# Deploy heapster to enable container cluster monitoring and performance analysis on your cluster
kubectl apply -f https://raw.githubusercontent.com/kubernetes/heapster/master/deploy/kube-config/influxdb/heapster.yaml

# Deploy the influxdb backend for heapster to your cluster
kubectl apply -f https://raw.githubusercontent.com/kubernetes/heapster/master/deploy/kube-config/influxdb/influxdb.yaml

# Create the heapster cluster role binding for the dashboard
kubectl apply -f https://raw.githubusercontent.com/kubernetes/heapster/master/deploy/kube-config/rbac/heapster-rbac.yaml 


#
# Step 2. Create an eks-admin Service Account and Cluster Role Binding
#


# Apply the service account and cluster role binding to your cluster
kubectl apply -f eks-admin-service-account.yaml


#
# Step 3. Connect to the Dashboard
#

# Retrieve an authentication token for the eks-admin service account. 
# Copy the <authentication_token> value from the output. 
# You use this token to connect to the dashboard.
kubectl -n kube-system describe secret $(kubectl -n kube-system get secret | grep eks-admin | awk '{print $1}')

echo ""
echo "http://localhost:8001/api/v1/namespaces/kube-system/services/https:kubernetes-dashboard:/proxy/#!/login"
echo ""

# Start the kubectl proxy
kubectl proxy


ehco 'Open the following link with a web browser to access the dashboard endpoint:' 
echo 'http://localhost:8001/api/v1/namespaces/kube-system/services/https:kubernetes-dashboard:/proxy/#!/login'
echo 'Choose Token, paste the <authentication_token> output from the previous command into the Token field, and choose SIGN IN.'



