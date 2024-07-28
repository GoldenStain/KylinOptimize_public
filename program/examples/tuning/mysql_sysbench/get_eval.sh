#!/bin/bash

# Maximum number of iterations to wait
MAX_ITER=30
i=1

while [ $i -lt $MAX_ITER ]
do
    sleep $i

    # Check if the log file exists and contains the desired line
    if [ -f "PATH/sysbench_oltp_read_write.log" ]; then
        QPS=$(grep 'queries:' PATH/sysbench_oltp_read_write.log | awk -F '(' '{print $2}' | awk -F ' ' '{print $1}')
        
        # Check if QPS is a valid number
        if [[ ! -z "$QPS" ]] && [[ "$QPS" =~ ^[0-9]+(\.[0-9]+)?$ ]]; then
            echo "$QPS"
            exit 0
        fi
    fi
    
    i=$((i+1))
done

# If the script reaches here, it means it couldn't get the QPS value
echo "Error: Unable to get QPS value"
exit 1