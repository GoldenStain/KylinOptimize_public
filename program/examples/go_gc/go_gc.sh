#!/bin/sh

if [ "$#" -ne 1 ]; then
  echo "USAGE: $0 ITERATION"
  exit 1
fi

ITERATION=$1

export GOGC=1440
export GOMAXPROCS=56
for ((i = 0; i < ITERATION; i++)); do
  echo 3 >/proc/sys/vm/drop_caches
  go test crypto/ecdsa -run=Bench -benchmem -bench=BenchmarkSignP256
done
