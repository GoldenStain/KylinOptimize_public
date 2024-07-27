#!/usr/bin/bash
KAFKA_DIR=$KAFKA_DIR
KAFKA_PRODUCER_TEST=$KAFKA_DIR/bin/kafka-producer-perf-test.sh
KAFKA_CONSUMER_TEST=$KAFKA_DIR/bin/kafka-consumer-perf-test.sh
KAFKA_SERVER_IP='will be replaced after running prepare.sh'
KAFKA_SERVER_PORT=9092

function get_producer_test_result() {
    output=$(
        $KAFKA_PRODUCER_TEST \
            --topic kafka-benchmark \
            --throughput -1 \
            --num-records 1000000 \
            --record-size 1024 \
            --producer-props acks=all bootstrap.servers="$KAFKA_SERVER_IP":"$KAFKA_SERVER_PORT"
    )
    result_line=$(grep '1000000' <<<"$output")
    arr=($result_line)
    echo "${arr[3]}"
}

function get_consumer_test_result() {
    output=$(
        $KAFKA_CONSUMER_TEST \
            --topic kafka-benchmark \
            --broker-list "$KAFKA_SERVER_IP":"$KAFKA_SERVER_PORT" \
            --messages 1000000
    )
    result_line=$(awk 'FNR == 2' <<<"$output")
    IFS=',' read -r -a arr <<<"$result_line"
    echo "${arr[5]}"
}

producer_test_result=$(get_producer_test_result)
consumer_test_result=$(get_consumer_test_result)
sum=$(echo "$producer_test_result + $consumer_test_result" | bc)
echo "$sum" >/root/kafka_benchmark.log