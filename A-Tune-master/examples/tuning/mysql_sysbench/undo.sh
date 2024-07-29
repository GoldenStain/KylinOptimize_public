#!/bin/bash

path=$(
  cd "$(dirname "$0")"
  pwd
)

# 恢复文件内容
sed -i "s#$path#PATH#g" $path/mysql_sysbench_client.yaml
sed -i "s#$path#PATH#g" $path/get_eval.sh
sed -i "s#TABLES=.*#TABLES=#g" $path/mysql_sysbench_benchmark.sh
sed -i "s#TABLE_SIZE=.*#TABLE_SIZE=#g" $path/mysql_sysbench_benchmark.sh
sed -i "s#$path#PATH#g" $path/mysql_sysbench_benchmark.sh

sed -i "s#startworkload:.*#startworkload: \"\"#g" $path/mysql_sysbench_server.yaml
sed -i "s#stopworkload:.*#stopworkload: \"\"#g" $path/mysql_sysbench_server.yaml

sed -i 's/\/usr\/bin\/mysql/MySQL_EXEC_PATH/g' $path/set_params.sh
sed -i 's|/usr/bin/mysql|MySQL_EXEC_PATH|g' $path/server.yaml
sed -i 's/\/usr\/local\/mysql\/bin\/mysql/MySQL_EXEC_PATH/g' $path/set_params.sh
sed -i 's|/usr/local/mysql/bin/mysql|MySQL_EXEC_PATH|g' $path/server.yaml
sed -i "s#$path#PATH#g" $path/server.yaml
#restore the password
sed -i "s#-p[^ ]*#-pPASSWORD#g" $path/set_params.sh

# 删除软链接，如果存在
if [ -L /etc/init.d/mysql ]; then
  rm /etc/init.d/mysql
  echo "Removed symlink /etc/init.d/mysql"
fi

# 删除添加的路径
cmd_remove_path="export PATH=$(echo $PATH | sed -e 's|:/usr/local/mysql/bin||')"
eval $cmd_remove_path

# 删除libmysqlclient.so.24的链接
if [ -L /usr/lib64/libmysqlclient.so.24 ]; then
  rm /usr/lib64/libmysqlclient.so.24
  echo "Removed symlink /usr/lib64/libmysqlclient.so.24"
fi

# 删除复制到的文件
if [ -f /etc/atuned/tuning/mysql_sysbench_server.yaml ]; then
  rm /etc/atuned/tuning/mysql_sysbench_server.yaml
  echo "Removed /etc/atuned/tuning/mysql_sysbench_server.yaml"
  cp $path/server.yaml /etc/atuned/tuning/mysql_sysbench_server.yaml
fi

echo "Undo script executed successfully."