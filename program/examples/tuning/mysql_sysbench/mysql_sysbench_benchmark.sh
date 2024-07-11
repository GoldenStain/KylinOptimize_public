#!/bin/sh

TABLES=10
TABLE_SIZE=100000

while true
do
    sysbench --config-file=sysbench_config.cfg oltp_read_write --tables=$TABLES --table-size=$TABLE_SIZE --time=30 prepare
    ret=$?
    if [ $ret == 0 ];then
        break
    fi
done

taskset -c 2,3 sysbench --config-file=sysbench_config.cfg oltp_read_write --tables=$TABLES --table-size=$TABLE_SIZE --time=300 --mysql-ignore-errors=8005 run  > /home/wsw/桌面/KylinDBOptimize/program/examples/tuning/mysql_sysbench//sysbench_oltp_read_write.log
count=0
while true
do
    val=$(cat /home/wsw/桌面/KylinDBOptimize/program/examples/tuning/mysql_sysbench/sysbench_oltp_read_write.log  | grep 'queries:' | awk -F '(' '{print $2}' | awk -F ' ' '{print $1}')
    if [ $val != "" ];then
        break
    elif [ $count == 10 ];then
        break
    else
        count=$(($count+1))
        sleep 3
    fi
done

sysbench --config-file=sysbench_config.cfg oltp_read_write --tables=$TABLES --table-size=$TABLE_SIZE --mysql-ignore-errors=8005 cleanup