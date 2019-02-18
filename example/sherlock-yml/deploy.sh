#! /bin/bash


kubectl create -f sherlock-namespace.yaml

kubectl create -f sherlock-redis.yaml

kubectl create -f sherlock-api.yaml

kubectl create -f sherlock-tensorflow.yaml

