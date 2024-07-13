#!/bin/sh

cur=$(
  cd "$(dirname "$0")"
  pwd
)

echo "Update the CPU tuning client and server YAML files"

# 修改客户端配置文件
sed -i "s#cd cpu_benchmark/#cd $cur/#g" $cur/tuning_cpu_client.yaml

# 修改服务器配置文件
sed -i "s#.cpu_benchmark/Makefile# $cur/Makefile#g" $cur/tuning_cpu_server.yaml
cp tuning_cpu_server.yaml /etc/atuned/tuning/

echo "Download and compile CPU benchmark"

# 下载和编译 CPU 相关的基准测试程序
wget https://www.cs.virginia.edu/stream/FTP/Code/stream.c -O cpu_benchmark/stream.c
gcc -O2 -fopenmp cpu_benchmark/stream.c -o cpu_benchmark/stream_benchmark
