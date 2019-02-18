#! /bin/bash
if [ $1 ]
then 
  tag=":$1"
else
  tag=""	
fi

docker build -t kaihsianc/sherlock-tensorflow$tag .
docker push kaihsianc/sherlock-tensorflow$tag
