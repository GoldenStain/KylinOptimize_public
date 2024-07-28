#!/bin/sh

path=$(
  cd "$(dirname "$0")"
  pwd
)

echo "update the client and server yaml files"
sed -i "s#sh .*/go_gc.sh#sh $path/go_gc.sh#g" $path/go_gc_client.yaml
sed -i "s#cat .*/go_gc.sh#cat $path/go_gc.sh#g" $path/go_gc_server.yaml
sed -i "s#' .*/go_gc.sh#' $path/go_gc.sh#g" $path/go_gc_server.yaml

echo "copy the server yaml file to /etc/atuned/tuning/"
cp $path/go_gc_server.yaml /etc/atuned/tuning/
