#!/bin/sh

# 检查参数数量是否为 1，如果不是则显示用法并退出
if [ "$#" -ne 1 ]; then
  echo "USAGE: $0 ITERATION"
  exit 1
fi

# 迭代次数参数
ITERATION=$1

# 设置 Go 的垃圾回收比例
export GOGC=1440
# 设置 Go 运行时使用的最大 CPU 数量
export GOMAXPROCS=56
for ((i = 0; i < ITERATION; i++)); do
  echo 3 >/proc/sys/vm/drop_caches
   # 运行 Go 的性能测试，针对 `crypto/ecdsa` 包的 `BenchmarkSignP256` 基准测试
  go test crypto/ecdsa -run=Bench -benchmem -bench=BenchmarkSignP256
done
