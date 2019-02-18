#! /bin/bash

kubectl delete --all deployments --namespace=sherlock

kubectl delete --all services --namespace=sherlock

kubectl delete --all pods --namespace=sherlock

kubectl delete namespace sherlock
