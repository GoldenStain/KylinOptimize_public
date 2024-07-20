path=$(
  cd "$(dirname "$0")"
  pwd
)

installation="mysql"
sysbench_cfg="--with-mysql-libs=/usr/local/mysql/lib/ --with-mysql-includes=/usr/local/mysql/include/"
cmd_service_link="ln -s /usr/local/mysql/support-files/mysql.server /etc/init.d/mysql"
cmd_add_path="export PATH=`echo $PATH`:/usr/local/mysql/bin"
new_password=123456


eval $cmd_service_link
mkdir -p /usr/local/mysql/{data,tmp,run,log}
chown -R mysql:mysql /usr/local/mysql

if [ -f /etc/my.cnf ]; then
  read -p "/etc/my.cnf 文件已存在，是否删除？ (y/n): " confirm
  if [ "$confirm" = "y" ]; then
    rm -rf /etc/my.cnf
    cp my.cnf /etc
  else
    echo "/etc/my.cnf 文件保留，继续执行脚本。"
  fi
fi
kill -9 `pidof mysqld`
eval $cmd_add_path
mysqld --user=root --initialize-insecure


systemctl daemon-reload
taskset -c 0,1 systemctl restart mysql

mysql -uroot << EOF
ALTER USER 'root'@'localhost' IDENTIFIED BY '${new_password}';
flush privileges;
use mysql;
update user set host='%' where user='root';
flush privileges;
create database sbtest;
quit
EOF

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

read -p "enter table_num of sysbench to used:" tables
read -p "enter table_size of sysbench to used:" table_size
echo "update the client and server yaml files"
sed -i "s#PATH#$path#g" $path/mysql_sysbench_client.yaml
sed -i "s#PATH#$path#g" $path/get_eval.sh
sed -i "s#TABLES=.*#TABLES=$tables#g" $path/mysql_sysbench_benchmark.sh
sed -i "s#TABLE_SIZE=.*#TABLE_SIZE=$table_size#g" $path/mysql_sysbench_benchmark.sh
sed -i "s#PATH#$path#g" $path/mysql_sysbench_benchmark.sh



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