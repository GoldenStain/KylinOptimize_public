#!/bin/sh
# Copyright (c) lingff(ling@stu.pku.edu.cn),
# School of Software & Microelectronics, Peking University.
#
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
#
# Create: 2021-05-24


TABLES=
TABLE_SIZE=

log_file="PATH/sysbench_oltp_read_write.log"

# Prepare phase
sysbench --config-file=sysbench_config.cfg /usr/share/sysbench/oltp_read_write.lua --tables=$TABLES --table-size=$TABLE_SIZE prepare

# Run phase

taskset -c 2,3 sysbench --config-file=sysbench_config.cfg /usr/share/sysbench/oltp_read_write.lua --tables=$TABLES --table-size=$TABLE_SIZE --time=100 --mysql-ignore-errors=8005 run > $log_file 2>&1
# sysbench --config-file=sysbench_config.cfg /usr/share/sysbench/oltp_read_write.lua --tables=$TABLES --table-size=$TABLE_SIZE --time=100 --mysql-ignore-errors=8005 run > $log_file 2>&1
ret=$?
if [ $ret -ne 0 ]; then
    echo "Sysbench run phase failed with return code $ret."
    exit $ret
fi

count=0
while true
do
    val=$(grep 'queries:' $log_file | awk -F '(' '{print $2}' | awk -F ' ' '{print $1}')
    if [ -n "$val" ]; then
        echo "Run phase completed successfully with queries: $val"
        break
    elif [ $count -eq 10 ]; then
        echo "Run phase failed to complete after 10 attempts."
        break
    else
        count=$((count+1))
        sleep 3
        echo "Waiting for run phase to complete... Attempt $count"
    fi
done

# Cleanup phase
sysbench --config-file=sysbench_config.cfg /usr/share/sysbench/oltp_read_write.lua --tables=$TABLES --table-size=$TABLE_SIZE --mysql-ignore-errors=8005 cleanup