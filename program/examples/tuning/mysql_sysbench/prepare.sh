path=$(
  cd "$(dirname "$0")"
  pwd
)

installation="mysql"
sysbench_cfg="--with-mysql-libs=/usr/local/mysql/lib/ --with-mysql-includes=/usr/local/mysql/include/"
cmd_service_link="ln -s /usr/local/mysql/support-files/mysql.server /etc/init.d/mysqld"
cmd_add_path="export PATH=`echo $PATH`:/usr/local/mysql/bin"


echo "install MySQL..."
# yum install -y $installation
rm -rf /etc/init.d/mysql
eval $cmd_service_link
mkdir -p /usr/local/mysql/{data,tmp,run,log}
chown -R mysql:mysql /usr/local/mysql


echo "initializing MySQL..."
rm -rf /etc/my.cnf
cp my.cnf /etc
kill -9 `pidof mysqld`
rm -rf /usr/local/mysql/data/*
eval $cmd_add_path
mysqld --initialize --user=mysql


echo "start MySQL..."
systemctl daemon-reload
taskset -c 0,1 systemctl restart mysql


echo -n "Enter current root password for MySQL: "
read -s current_password
echo    # move to a new line after inputting password

echo -n "Enter new root password for MySQL(123456): "
read -s new_password
echo    # move to a new line after inputting password

# Use mysqladmin to set the new password
mysqladmin -uroot -p"${current_password}" password "${new_password}"

echo "create database..."
mysql -uroot -p"${new_password}" << EOF
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


echo "install sysbench..."
yum install -y git
git clone --depth=1 https://github.com/akopytov/sysbench.git
cd sysbench
yum install -y automake libtool
./autogen.sh
./configure $sysbench_cfg
make -j
make install


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



sed -i "s#startworkload:.*#startworkload: \"taskset -c 0,1 systemctl start mysql\" #g" $path/server.yaml
sed -i "s#stopworkload:.*#stopworkload: \"systemctl stop mysql\" #g" $path/server.yaml


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