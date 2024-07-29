#!/bin/sh

path=$(
  cd "$(dirname "$0")"
  pwd
)
echo "current run path is $path"

tune=generic
option=O0
array_size=20000000
times=10
offset=1024
isarch=no
if [[ $isarch == "yes" ]]; then
  arch="-march=native"
fi
isopenmp=no
if [[ $isopenmp == "yes" ]]; then
  openmp="-fopenmp"
fi

gcc -mtune=$tune $arch -$option $openmp -DSTREAM_ARRAY_SIZE=$array_size -DNTIMES=$times -DOFFSET=$offset $path/stream.c -o $path/stream.o
$path/stream.o
echo "file size: `wc -c $path/stream.o`"
rm -rf $path/stream.o
