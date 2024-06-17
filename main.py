#!/usr/bin/python3.7m
from program.server import app, client
import threading
from program.ebpf import flame_graph, data_sample
import argparse
import time

parser = argparse.ArgumentParser(description="eBPF based Database System Optimizer")
parser.add_argument('-p', '--port', type=int, default=5000, help='local HTTP server port')
args = parser.parse_args()

port = args.port

threading.Thread(target=lambda: app.start(port), daemon=True).start()
threading.Thread(target=lambda: client.start(port)).start()
threading.Thread(target=lambda: data_sample.start(), daemon=True).start()

#flame_graph.gen_cpu_flame_graph("server/out", 30)

print("按下Ctrl+C终止程序")
try:
    while True:
        time.sleep(1.0)
        pass
except KeyboardInterrupt:
    print("程序终止")

