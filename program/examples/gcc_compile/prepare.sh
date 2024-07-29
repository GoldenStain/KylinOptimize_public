#!/bin/sh

path=$(
  cd "$(dirname "$0")"
  pwd
)

echo "update the client and server yaml files"
sed -i "s#sh .*/gcc_compile.sh#sh $path/gcc_compile.sh#g" $path/gcc_compile_client.yaml
sed -i "s#cat .*/gcc_compile.sh#cat $path/gcc_compile.sh#g" $path/gcc_compile_server.yaml
sed -i "s#' .*/gcc_compile.sh#' $path/gcc_compile.sh#g" $path/gcc_compile_server.yaml

echo "copy the server yaml file to /etc/atuned/tuning/"
cp $path/gcc_compile_server.yaml /etc/atuned/tuning/
