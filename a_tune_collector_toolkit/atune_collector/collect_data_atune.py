#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2020 Huawei Technologies Co., Ltd.
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2020-11-13

"""
The main function for collecting data.
"""
import argparse
import json
import os
import time
import csv
import subprocess
import sys
import threading

from plugin.plugin import MPI
from werkzeug.utils import secure_filename


class Collector:
    """class for Collector"""

    def __init__(self, data):
        self.data = data
        self.field_name = []
        self.support_multi_block = ['storage']
        self.support_multi_nic = ['network', 'network-err']
        self.support_multi_app = ['process']
        self.monitors = self.parse_json()
        self.mpi = MPI()

    def parse_json(self):
        """parse json data"""
        monitors = []
        for item in self.data["collection_items"]:
            if item["name"] in self.support_multi_app and ('application' not in self.data or
                                                                self.data["application"] == ""):
                continue
            if item["name"] in self.support_multi_app:
                applications = self.data["application"].split(',')
                parameters = ["--interval=%s --app=%s;" %(self.data["interval"], self.data["application"])]
                for application in applications:    
                    for metric in item["metrics"]:
                        self.field_name.append(
                            "%s.%s.%s#%s" % (item["module"], item["purpose"], metric, application))
                        parameters.append("--fields=%s" % metric)
            else:
                parameters = ["--interval=%s;" % self.data["interval"]]
                for metric in item["metrics"]:
                    nics = self.data["network"].split(',')
                    blocks = self.data["block"].split(',')
                    
                    if item["name"] in self.support_multi_nic and len(nics) > 1:
                        for net in nics:
                            self.field_name.append(
                                "%s.%s.%s#%s" % (item["module"], item["purpose"], metric, net))
                    elif item["name"] in self.support_multi_block and len(blocks) > 1:
                        for block in blocks:
                            self.field_name.append(
                                "%s.%s.%s#%s" % (item["module"], item["purpose"], metric, block))
                    else:
                        self.field_name.append("%s.%s.%s" % (item["module"], item["purpose"], metric))
                    parameters.append("--fields=%s" % metric)
                if "threshold" in item:
                    parameters.append("--threshold=%s" % item["threshold"])

            parameters.append("--nic=%s" % self.data["network"])
            parameters.append("--device=%s" % self.data["block"])
            monitors.append([item["module"], item["purpose"], " ".join(parameters)])
        return monitors

    def collect_data(self):
        """collect data"""
        raw_data = self.mpi.get_monitors_data(self.monitors)
        float_data = [float(num) for num in raw_data]
        return float_data

TABLE_SIZE = '100000'

commands = [
    ['sysbench', 'cpu', '--cpu-max-prime=20000000', '--threads=14', '--time=120', 'run'],
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
    ],
    [
        'sysbench',
        '--db-driver=mysql',
        '--mysql-db=sbtest',
        '--mysql-user=root',
        '--mysql-password=mysql123456',
        '--table-size=' + TABLE_SIZE,
        '--tables=10',
        '--threads=14',
        '--time=120',
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
		'/home/xjbo/桌面/inch/inch',
    	'-b', '1000',
    	'-c', '14',
    	'-db', 'Stress',
    	'-host', 'http://localhost:8086',
    	'-p', '1000',
    	'-m', '5',
    	'-t', '100,10',
        '-f', '3',
    	'-token', 'bvYd9DG4n5IlVLUKLIeay7zJkxrhJRFVXmCIbuJPaff_5cHknvUPKmaK6urdRQLRDRVHsXFh2Umuwro6lb4I6g==',
    	'-vhosts', '8',
    	'-v', '--v2',
        '-time', '600s',
        '-shard-duration', '1h'
	],# 4
    ['stress-ng', '--vm', '2', '--vm-bytes', '8G', '--vm-method', 'all', '--verify', '-t', '90s'],
    ['sysbench', 'fileio', '--file-total-size=10G', 'prepare'],
    ['sysbench', 'fileio', '--file-total-size=10G', '--file-test-mode=rndrw', '--time=120', '--max-requests=0', 'run'],
    ['sysbench', 'fileio', '--file-total-size=10G', 'cleanup'],#8
    ['iperf3', '-c', '127.0.0.1', '-b', '10000M', '-t', '120']
]

stress_process = None
stress_lock = threading.Lock()

def start_stress():
    global stress_process
    stress_process = subprocess.Popen(commands[0], stdout=sys.stdout, stderr=sys.stderr, text=True)

def mySQL_stress():
    global stress_process
    # 启动 prepare_process 并等待其结束
    prepare_process = subprocess.Popen(commands[1], stdout=sys.stdout, stderr=sys.stderr, text=True)
    prepare_process.wait()
    # 启动 stress_process
    with stress_lock:
        stress_process = subprocess.Popen(commands[2], stdout=sys.stdout, stderr=sys.stderr, text=True)
    stress_process.wait()
    subprocess.run(commands[3], stdout=sys.stdout, stderr=sys.stderr, text=True)

def mySQL_prepare():
    global stress_process
    # 预先创建一个占位的 subprocess 对象
    with stress_lock:
        stress_process = subprocess.Popen(['sleep', 'infinity'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, text=True)
    stress_thread = threading.Thread(target=mySQL_stress)
    stress_thread.start()

def fileio_stress():
    global stress_process
    prepare_process = subprocess.Popen(commands[6], stdout=sys.stdout, stderr=sys.stderr, text=True)
    prepare_process.wait()
    # 启动 stress_process
    with stress_lock:
        stress_process = subprocess.Popen(commands[7], stdout=sys.stdout, stderr=sys.stderr, text=True)
    stress_process.wait()
    subprocess.run(commands[8], stdout=sys.stdout, stderr=sys.stderr, text=True)

def fileio_prepare():
    global stress_process
    with stress_lock:
        stress_process = subprocess.Popen(['sleep', 'infinity'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, text=True)
    stress_thread = threading.Thread(target=fileio_stress)
    stress_thread.start()

def influxDB_stress():
    global stress_process
    with stress_lock:
        stress_process = subprocess.Popen(commands[4], stdout=sys.stdout, stderr=sys.stderr, text=True)
    
def memory_stress():
    global stress_process
    with stress_lock:
        stress_process = subprocess.Popen(commands[5], stdout=sys.stdout, stderr=sys.stderr, text=True)

def net_stress():
    global stress_process
    with stress_lock:
        stress_process = subprocess.Popen(commands[9], stdout=sys.stdout, stderr=sys.stderr, text=True)

def start_collect_atune(arg_json_path):
    current_user = os.getlogin()
    json_path = "./a_tune_collector_toolkit/atune_collector/collect_data.json"
    if arg_json_path:
        json_path = arg_json_path
    with open(json_path, 'r') as file:
        json_data = json.load(file)
    filename = secure_filename(json_path)
    collector = Collector(json_data)
    path = os.path.abspath(os.path.expanduser(os.path.expandvars(collector.data["output_dir"])))
    if not os.path.exists(path):
        os.makedirs(path, 0o750)
    try:
        collect_num = collector.data["sample_num"]
        if int(collect_num) < 1:
            os.abort("sample_num must be greater than 0")
        file_name = "{}-{}.csv".format(collector.data.get("workload_type", "default"), int(round(time.time() * 1000)))

        print("csv path: %s" % os.path.join(path, file_name))
        print("csv fields: %s" % " ".join(collector.field_name))
        print("start to collect data...")

        # stress test !!!
        memory_thread = threading.Thread(target=memory_stress)
        memory_thread.start()

        with open(os.path.join(path, file_name), "w") as csvfile:
            writer = csv.writer(csvfile)
            output_fields = ["TimeStamp"] + collector.field_name
            writer.writerow(output_fields)
            csvfile.flush()
            for _ in range(collect_num):
                data = collector.collect_data()
                str_data = [str(round(value, 3)) for value in data]
                str_data.insert(0, time.strftime("%H:%M:%S"))
                writer.writerow(str_data)
                csvfile.flush()
                with stress_lock:
                    if stress_process.poll() is not None:
                        break
                # print(" ".join(str_data))
        print("finish to collect data, csv path is %s" % os.path.join(path, file_name))

    except KeyboardInterrupt:
        print("user stop collect data")

    subprocess.run(['chown', current_user, f'{path}/{file_name}'], capture_output=False)