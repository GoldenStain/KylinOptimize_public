#!/usr/bin/python3.7m
from server import app
#from server import client
import threading
from ebpf import flame_graph
import argparse

parser = argparse.ArgumentParser(description="eBPF based Database System Optimizer")
parser.add_argument('-p', '--port', type=int, default=5000, help='local HTTP server port')
args = parser.parse_args()

port = args.port

threading.Thread(target=lambda: app.start()).start()
#threading.Thread(target=lambda: client.start()).start()

#flame_graph.gen_cpu_flame_graph("server/out", 30)

