#!/usr/bin/python3.7m
# encoding=utf-8
import subprocess
from bcc import BPF
import ctypes
import time
import argparse
import os
import threading
import sys

def read_sysbench_output(process):
    """Read the output from the sysbench process and print it to stdout."""
    for line in iter(process.stdout.readline, ''):
        print(line.strip())
    process.stdout.close()

TABLE_SIZE = '10000'

parser = argparse.ArgumentParser(description="eBPF data collector")
parser.add_argument('-p', '--pid', type=int, default=0, help='target process PID')
parser.add_argument('-f', '--function', type=int, default=0, help='choose the function')
args = parser.parse_args()

t_pid = args.pid
para_in = args.function

# 记录测试次数的文件路径
test_count_file = 'test_count.txt'

# 检查记录测试次数的文件是否存在，不存在则创建并初始化为0
if not os.path.exists(test_count_file):
    with open(test_count_file, 'w') as f:
        f.write('0')

# 读取当前测试次数
with open(test_count_file, 'r') as f:
    test_count = f.read().strip()
    if test_count:
        test_count = int(test_count)
    else:
        test_count = 0

# 增加测试次数
test_count += 1

# 保存新的测试次数
with open(test_count_file, 'w') as f:
    f.write(str(test_count))

# 定义 sysbench 命令和参数
commands = [
    [
        '/home/xjbo/桌面/inch/inch',
        '-b',
        '1000',
        '-c',
        '10',
        '-db',
        'stress',
        '-host',
        'http://localhost:8086',
        '-p',
        '1000',
        '-m',
        '5',
        '-t',
        '100,100,100',
        '-token',
        'bvYd9DG4n5IlVLUKLIeay7zJkxrhJRFVXmCIbuJPaff_5cHknvUPKmaK6urdRQLRDRVHsXFh2Umuwro6lb4I6g==',
        '-v',
        '--v2'
    ]
]

# 将 sysbench 命令转换为字符串
command_str = ' '.join(commands[para_in][-4:]) + " interval = 0.5s"

# 生成csv文件名
csv_filename = f"mysql_result/output{test_count}.csv"

# 创建mysql_result文件夹，如果不存在
os.makedirs('mysql_result', exist_ok=True)

# 打开csv文件进行写入
with open(csv_filename, 'w', encoding='utf-8') as csv:
    headers = ["TCP_sent", "TCP_recv", "DISK_read", "DISK_write", "DISK_read_cnt", "DISK_write_cnt", "CPU_usage"]
    csv.write(','.join(headers) + '\n')

os.chown(csv_filename, 1000, 1000)

# 打印文件路径
print(f"测试结果保存在文件：{csv_filename}")

bpf = BPF(src_file="bpf_data.c")
bpf.attach_kprobe(event="tcp_sendmsg", fn_name="trace_tcp_sendmsg")
bpf.attach_kprobe(event="tcp_recvmsg", fn_name="trace_tcp_recvmsg")
bpf.attach_kprobe(event="blk_account_io_start", fn_name="trace_block_rq_insert")
bpf.attach_kprobe(event="blk_mq_complete_request", fn_name="trace_disk_read")
bpf.attach_kprobe(event="finish_task_switch", fn_name="kprobe__finish_task_switch")

send_bytes = bpf["send_bytes"]
recv_bytes = bpf["recv_bytes"]

disk_read_bytes = bpf["disk_read_bytes"]
disk_write_bytes = bpf["disk_write_bytes"]
disk_read_count = bpf["disk_read_count"]
disk_write_count = bpf["disk_write_count"]

cpu_usage = bpf["cpu_usage"]
mem_usage = bpf["mem_usage"]

def collect_data():
    print('数据采集开始，输入Ctrl+C结束')
    while process.poll() is None:  # 检查 sysbench 进程是否结束
        time.sleep(0.5)

        TCP_sent = 0
        TCP_recv = 0
        DISK_read = 0
        DISK_write = 0
        DISK_read_cnt = 0
        DISK_write_cnt = 0
        CPU_usage = 0
        MEM_usage = 0

        for k, v in send_bytes.items():
            pid = k.value
            bytes_sent = v.value
            if t_pid == 0 or pid == t_pid:
                TCP_sent += bytes_sent
            #print(f"Process {pid} sent {bytes_sent} bytes")
        for k, v in recv_bytes.items():
            pid = k.value
            bytes_recv = v.value
            if t_pid == 0 or pid == t_pid:
                TCP_recv += bytes_recv
            #print(f"Process {pid} received {bytes_recv} bytes")
        
        for k, v in disk_read_bytes.items():
            pid = k.value
            value = v.value
            if t_pid == 0 or pid == t_pid:
                DISK_read += value
        for k, v in disk_write_bytes.items():
            pid = k.value
            value = v.value
            if t_pid == 0 or pid == t_pid:
                DISK_write += value
        for k, v in disk_read_count.items():
            pid = k.value
            value = v.value
            if t_pid == 0 or pid == t_pid:
                DISK_read_cnt += value
        for k, v in disk_write_count.items():
            pid = k.value
            value = v.value
            if t_pid == 0 or pid == t_pid:
                DISK_write_cnt += value
        
        for k, v in cpu_usage.items():
            pid = k.value
            value = v.value
            if t_pid == 0 or pid == t_pid:
                CPU_usage += value
        CPU_usage /= 1e9

        # for k, v in mem_usage.items():
        # 	pid = k.value
        # 	value = v.value
        # 	if t_pid == 0 or pid == t_pid:
        # 		MEM_usage += value

        send_bytes.clear()
        recv_bytes.clear()

        disk_read_bytes.clear()
        disk_write_bytes.clear()
        disk_read_count.clear()
        disk_write_count.clear()

        cpu_usage.clear()
        
        line = ','.join(map(str, [TCP_sent, TCP_recv, DISK_read, DISK_write, DISK_read_cnt, DISK_write_cnt, CPU_usage]))
        with open(csv_filename, 'a', encoding='utf-8') as csv:
            csv.write(line + '\n')

        print(line)

# 启动 sysbench 命令，不阻塞主线程
process = subprocess.Popen(commands[para_in], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

# 启动一个线程来读取 sysbench 的输出并打印到标准输出
threading.Thread(target=read_sysbench_output, args=(process,), daemon=True).start()

print("Sysbench command is running...")

# 启动数据采集线程
data_thread = threading.Thread(target=collect_data)
data_thread.start()

# 在捕获到 KeyboardInterrupt 后，将 sysbench 命令作为标签写入 CSV 文件
with open(csv_filename, 'a', encoding='utf-8') as csv:
    csv.write(f"TEST_INFO: {command_str}\n")
