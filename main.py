#!/usr/bin/python3.7m
# encoding=utf-8
from program.server import app, client
import threading
from program.ebpf import flame_graph, data_sample
from program.tools import bpf_data
import argparse
import time
import subprocess
from program.a_tune_collector_toolkit.atune_collector import collect_data_atune
from program.server import logger

useable_workload = ['centralized database', 'CPUstress', 'default', 'distributed databases', 'fileio stress', 'memory stress', 'net stress']

parser = argparse.ArgumentParser(description="eBPF based Database System Optimizer")
parser.add_argument('-d', '--data-sample', action='store_true', default=False, help='sample data only')
parser.add_argument('-v', '--verbose', action='store_true', default=False, help='show more information')
parser.add_argument('--flame-graph', action='store_true', default=False, help='generate performance flame graph')
parser.add_argument('-p', '--port', type=int, default=80, help='local HTTP server port')
parser.add_argument('--pid', type=int, default=0, help='target pid to sample data')
parser.add_argument('-a', '--atune', action='store_true', default=False, help='collect data for Atune')
parser.add_argument('-c', '--confidence', action='store_true', default=False, help='calculate confidence')
parser.add_argument('--type', type=str, default=None, help = 'specify the workload type')
args = parser.parse_args()

is_verbose = args.verbose
port = args.port
pid = args.pid
work_type = args.type

def IO_monitor():
    subprocess.run(collect_data_atune.commands[1])
    IO_thread = threading.Thread(target=collect_data_atune.mySQL_stress)
    flame_thread = threading.Thread(target=flame_graph.gen_flame_graph_perf,args=["program/server/static/flame_graph", 50, 10, [1951, 2278]])
    IO_thread.start()
    flame_thread.start()
    IO_thread.join()
    flame_thread.join()

if work_type is not None and work_type not in useable_workload:
    print('请输入合法的work_type')
    exit(1)

if args.atune:
    collect_data_atune.collector_collect_data(work_type)
    exit(0)

if args.confidence:
    print(collect_data_atune.get_data_return_confidence())
    exit(0)

if args.data_sample:
    bpf_data.start(t_pid=pid, verbose=is_verbose)
    exit(0)

if args.flame_graph:
    #flame_graph.gen_cpu_flame_graph("program/server/static/flame_graph", 50)
    flame_graph.gen_flame_graph_perf("program/server/static/flame_graph", 50)
    # IO_monitor()
    exit(0)

threading.Thread(target=lambda: app.start(port), daemon=True).start()
logger.log_info('Server Started')
threading.Thread(target=lambda: client.start(port)).start()
logger.log_info('Client Started')
threading.Thread(target=lambda: data_sample.start(), daemon=True).start()
logger.log_info('Data Sampler Started')

print("按下Ctrl+C终止程序")
try:
    while True:
        time.sleep(1.0)
        pass
except KeyboardInterrupt:
    print("程序终止")
    logger.log_info('Program Stopped')

