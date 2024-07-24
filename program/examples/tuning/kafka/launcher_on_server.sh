#!/usr/bin/bash
echo 'launch benchmark'

WORKING_DIR="will be replaced after running prepare.sh"
KAFKA_CLIENT_IP='will be replaced after running prepare.sh'

if [ -f "./client_ssh_key" ]; then
    ssh -i $WORKING_DIR/client_ssh_key root@"$KAFKA_CLIENT_IP" -t "/usr/bin/bash /root/benchmark_on_client.sh"
    scp -i $WORKING_DIR/client_ssh_key root@"$KAFKA_CLIENT_IP":/root/kafka_benchmark.log ./
else
    ssh root@"$KAFKA_CLIENT_IP" -t "/usr/bin/bash /root/benchmark_on_client.sh"
    scp root@"$KAFKA_CLIENT_IP":/root/kafka_benchmark.log ./
fi