#!/usr/bin/python3.7m
# encoding=utf-8

from bcc import BPF
import ctypes
import time
import argparse
from ..ebpf import data_sample
import os
import subprocess
import threading

TABLE_SIZE = '3000'
test_count = 0
benchmark_process = None
csv = None

commands = [
    [
        'sysbench',
        '--db-driver=mysql',
        '--mysql-db=sbtest',
        '--mysql-user=root',
        '--mysql-password=mysql123456',
        '--table-size=' + TABLE_SIZE,
        '--tables=10',
        # '--threads=20',
        '/usr/share/sysbench/oltp_read_write.lua',
        'run'
    ],
    [
        'sysbench',
        '--db-driver=mysql',
        '--mysql-db=sbtest',
        '--mysql-user=root',
        '--mysql-password=mysql123456',
        '--tables=10',
        '/usr/share/sysbench/oltp_read_write.lua',
        'cleanup'
    ],
    [
        'sysbench',
        '--db-driver=mysql',
        '--mysql-db=sbtest',
        '--mysql-user=root',
        '--mysql-password=mysql123456',
        '--table-size=' + TABLE_SIZE,
        '--tables=10',
        '/usr/share/sysbench/oltp_read_write.lua',
        'prepare'
    ]
]

def get_test_count():
	global test_count
	test_count_file = 'test_count.txt'
	if not os.path.exists(test_count_file):
		with open(test_count_file, 'w') as f:
			f.write('0')
	with open(test_count_file, 'r') as f:
		test_count = f.read().strip()
		if test_count:
			test_count = int(test_count)
		else:
			test_count = 0
	test_count += 1
	with open (test_count_file, 'w') as f:
		f.write(str(test_count))

# 压力测试函数
def bench_task():
	global benchmark_process
	output_file = 'benchmark_output.txt'
	with open(output_file, 'w') as f:
		result = subprocess.run(commands[2], stdout=f, stderr=f, text=True)
	print(f"The output of benchmark has been redirected to {output_file}")
	with open(output_file, 'a') as f:
		benchmark_process = subprocess.Popen(commands[0], stdout=f, stderr=f, text=True)

def bpf_data_collect(t_pid=None, verbose=False):
	global csv
	result_dir = "mysql_result"
	if not os.path.exists(result_dir):
		os.makedirs(result_dir)
	csv = open(f"{result_dir}/bpf_data{test_count}.csv", "w")

	bpf = data_sample.init_ebpf()
	dicts = data_sample.get_dicts(bpf)

	headers = [k for k in dicts]
	if not t_pid:
		headers.append("procs")
	csv.write(','.join(headers) + '\n')



	print('数据采集开始，输入Ctrl+C结束')
	print('\t'.join(headers))

	while benchmark_process.poll() is None:
		try:
			time.sleep(0.2)

			data_list = []

			if not t_pid:
				data = data_sample.get_sum(dicts)
				for k in dicts:
					data_list.append(data[k])
			else:
				data = data_sample.get_pid_sum(dicts, t_pid)
				for k in dicts:
					data_list.append(data[k]) 
				
			if not t_pid:
				# 这里活跃进程为持续时间大于1秒的进程数
				data_list.append(len(dicts))

			data_sample.clear_dicts(bpf, dicts)
			csv.write(','.join(map(str, data_list)) + '\n')

			if verbose:
				print('\t'.join(map(str, data_list)))

		except KeyboardInterrupt:
			print('数据采集结束')
			exit()

def start(t_pid=None, verbose=False):
	get_test_count()
	collect_thread = threading.Thread(target=bpf_data_collect, args=(t_pid, verbose))
	bench_task()
	collect_thread.start()
	benchmark_process.wait()
	collect_thread.join()
	csv.write(f"TABLES: 10\nTABLE_SIZE: {TABLE_SIZE}\n")
	csv.close()
	with open("benchmark_output.txt", 'a') as f:
		subprocess.run(commands[1],stdout=f, stderr=f, text=True)


	
	

