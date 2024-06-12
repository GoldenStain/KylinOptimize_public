#!/usr/bin/python3.7m
# encoding=utf-8

from bcc import BPF
import ctypes
import time
import argparse

parser = argparse.ArgumentParser(description="eBPF data collector")
parser.add_argument('-p', '--pid', type=int, default=0, help='target process PID')
args = parser.parse_args()

t_pid = args.pid

csv = open("output.csv", "w")
headers = ["TCP_sent", "TCP_recv", "DISK_read", "DISK_write", "DISK_read_cnt", "DISK_write_cnt"]

csv.write(','.join(headers) + '\n')

bpf = BPF(src_file="bpf_data.c")
bpf.attach_kprobe(event="tcp_sendmsg", fn_name="trace_tcp_sendmsg")
bpf.attach_kprobe(event="tcp_recvmsg", fn_name="trace_tcp_recvmsg")
bpf.attach_kprobe(event="blk_account_io_start", fn_name="trace_block_rq_insert")

send_bytes = bpf["send_bytes"]
recv_bytes = bpf["recv_bytes"]

disk_read_bytes = bpf["disk_read_bytes"]
disk_write_bytes = bpf["disk_write_bytes"]
disk_read_count = bpf["disk_read_count"]
disk_write_count = bpf["disk_write_count"]

print('数据采集开始，输入Ctrl+C结束')

while True:
	try:
		time.sleep(1.0)

		TCP_sent = 0
		TCP_recv = 0
		DISK_read = 0
		DISK_write = 0
		DISK_read_cnt = 0
		DISK_write_cnt = 0

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
		
		for k, v, in disk_read_bytes.items():
			pid = k.value
			value = v.value
			if t_pid == 0 or pid == t_pid:
				DISK_read += value
		for k, v, in disk_write_bytes.items():
			pid = k.value
			value = v.value
			if t_pid == 0 or pid == t_pid:
				DISK_write += value
		for k, v, in disk_read_count.items():
			pid = k.value
			value = v.value
			if t_pid == 0 or pid == t_pid:
				DISK_read_cnt += value
		for k, v, in disk_write_count.items():
			pid = k.value
			value = v.value
			if t_pid == 0 or pid == t_pid:
				DISK_write_cnt += value

		send_bytes.clear()
		recv_bytes.clear()

		disk_read_bytes.clear()
		disk_write_bytes.clear()
		disk_read_count.clear()
		disk_write_count.clear()
		
		line = ','.join(map(str, [TCP_sent, TCP_recv, DISK_read, DISK_write, DISK_read_cnt, DISK_write_cnt]))
		csv.write(line + '\n')

		print(line)

	except KeyboardInterrupt:
		print('数据采集结束')
		exit()

