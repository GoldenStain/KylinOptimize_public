#!/usr/bin/python3.7m
# encoding=utf-8
from program.server import app, client
import threading
from program.ebpf import flame_graph, data_sample
from program.tools import bpf_data
import argparse
import time
from program.a_tune_collector_toolkit.atune_collector import collect_data_atune

parser = argparse.ArgumentParser(description="eBPF based Database System Optimizer")
parser.add_argument('-d', '--data-sample', action='store_true', default=False, help='sample data only')
parser.add_argument('-v', '--verbose', action='store_true', default=False, help='show more information')
parser.add_argument('--flame-graph', action='store_true', default=False, help='generate performance flame graph')
parser.add_argument('-p', '--port', type=int, default=80, help='local HTTP server port')
parser.add_argument('--pid', type=int, default=0, help='target pid to sample data')
parser.add_argument('-a', '--atune', action='store_true', default=False, help='collect data for Atune')
parser.add_argument('-c', '--config', type=str, default=None, help='specific the location of collect_data.json')
args = parser.parse_args()

is_verbose = args.verbose
port = args.port
pid = args.pid

if(args.atune):
    collect_data_atune.start_collect_atune(args.config)
    # print(collect_data_atune.get_data_return_confidence())
    exit(0)

if args.data_sample:
    bpf_data.start(t_pid=pid, verbose=is_verbose)
    exit(0)

if args.flame_graph:
    #flame_graph.gen_cpu_flame_graph("program/server/static/flame_graph", 50)
    flame_graph.gen_flame_graph_perf("program/server/static/flame_graph", 50)
    exit(0)

threading.Thread(target=lambda: app.start(port), daemon=True).start()
threading.Thread(target=lambda: client.start(port)).start()
threading.Thread(target=lambda: data_sample.start(), daemon=True).start()

print("按下Ctrl+C终止程序")
try:
    while True:
        time.sleep(1.0)
        pass
except KeyboardInterrupt:
    print("程序终止")

