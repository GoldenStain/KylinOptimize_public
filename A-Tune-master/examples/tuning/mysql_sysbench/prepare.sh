path=$(
  cd "$(dirname "$0")"
  pwd
)


installation="mysql"
sysbench_cfg="--with-mysql-libs=/usr/local/mysql/lib/ --with-mysql-includes=/usr/local/mysql/include/"
cmd_service_link="ln -s /usr/local/mysql/support-files/mysql.server /etc/init.d/mysql"
cmd_add_path="export PATH=`echo $PATH`:/usr/local/mysql/bin"


if [ ! -L /etc/init.d/mysql ]; then
  eval $cmd_service_link
fi

eval $cmd_add_path


if [ ! -f /usr/lib64/libmysqlclient.so.* ]; then
    echo "ln libmysqlclient.so.24 to /usr/lib64"
    ln -s /usr/local/mysql/lib/libmysqlclient.so.24 /usr/lib64
fi


echo "checking sysbench..."
sysbench --version
if [ $? -ne 0 ]; then   
    echo "sysbench FAILED";   
    exit 1;   
fi

real_password=$(grep 'mysql-password=' $path/sysbench_config.cfg | cut -d '=' -f 2-)
read -p "enter table_num of sysbench to used:" tables
read -p "enter table_size of sysbench to used:" table_size
echo "update the client and server yaml files"
sed -i "s#PATH#$path#g" $path/mysql_sysbench_client.yaml
sed -i "s#PATH#$path#g" $path/get_eval.sh
sed -i "s#TABLES=.*#TABLES=$tables#g" $path/mysql_sysbench_benchmark.sh
sed -i "s#TABLE_SIZE=.*#TABLE_SIZE=$table_size#g" $path/mysql_sysbench_benchmark.sh
sed -i "s#PATH#$path#g" $path/mysql_sysbench_benchmark.sh
# replace the real password
sed -i "s#-p[^ ]*#-p$real_password#g" $path/set_params.sh



sed -i "s#startworkload:.*#startworkload: \"taskset -c 0,1 systemctl start mysql\" #g" $path/mysql_sysbench_server.yaml
sed -i "s#stopworkload:.*#stopworkload: \"systemctl stop mysql\" #g" $path/mysql_sysbench_server.yaml

echo "Setting the executable path of the MySQL database"
if [ -f /usr/bin/mysql ]; then
	sed -i 's/MySQL_EXEC_PATH/\/usr\/bin\/mysql/g' $path/set_params.sh
	sed -i 's|MySQL_EXEC_PATH|/usr/bin/mysql|g'    $path/server.yaml
elif [ -f /usr/local/mysql/bin/mysqld ]; then
	sed -i 's/MySQL_EXEC_PATH/\/usr\/local\/mysql\/bin\/mysql/g' $path/set_params.sh
	sed -i 's|MySQL_EXEC_PATH|/usr/local/mysql/bin/mysql|g'      $path/server.yaml
else
	echo "Setting failed! No available mysql executable file is found."
	exit 1
fi

echo "copy the server yaml file to /etc/atuned/tuning/"
rm -rf /etc/atuned/tuning/mysql_sysbench_server.yaml
sed -i "s#PATH#$path#g" $path/server.yaml
cp $path/server.yaml /etc/atuned/tuning/mysql_sysbench_server.yaml
