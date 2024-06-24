#!/usr/bin/python3.7m
# encoding=utf-8

from bcc import BPF
import ctypes
import time
import argparse
from ..ebpf import data_sample

def start(t_pid, verbose=False):
	csv = open("output.csv", "w")

	bpf = data_sample.init_ebpf()
	dicts = data_sample.get_dicts(bpf)

	headers = [k for k in dicts]
	if t_pid == 0:
		headers.append("procs")
	csv.write(','.join(headers) + '\n')

	print('数据采集开始，输入Ctrl+C结束')
	print('\t'.join(headers))

	while True:
		try:
			time.sleep(1.0)

			data_list = []

			if t_pid == 0:
				data = data_sample.get_sum(dicts)
				for k in dicts:
					data_list.append(data[k])
			else:
				data = data_sample.get_pid_sum(dicts, t_pid)
				for k in dicts:
					data_list.append(data[k]) 
				
			if t_pid == 0:
				# 这里活跃进程为持续时间大于1秒的进程数
				data_list.append(len(dicts))

			data_sample.clear_dicts(bpf, dicts)
			csv.write(','.join(map(str, data_list)) + '\n')

			if verbose:
				print('\t'.join(map(str, data_list)))

		except KeyboardInterrupt:
			print('数据采集结束')
			exit()

