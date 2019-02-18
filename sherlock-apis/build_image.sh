#! /bin/bash
if [ $1 ]
then 
  tag=":$1"
else
  tag=""	
fi

docker build -t kaihsianc/sherlock-api$tag .
docker push kaihsianc/sherlock-api$tag
