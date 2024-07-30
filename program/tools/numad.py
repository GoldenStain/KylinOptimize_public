import subprocess
import psutil
import time
import numpy as np

class NumadManager:
    def __init__(self, scan_type=1):
        self.scan_type = scan_type

    def start_numad(self):
        command = ['numad', '-S', str(self.scan_type)]
        self.numad_process = subprocess.Popen(command, shell=True)
    
    def stop_numad(self):
        self.numad_process.kill()
    
    def monitor_performance(self, duration=10):
        """监控系统性能"""
        cpu_usage = []
        mem_usage = []
        context_switches = []
        iowait = []

        for _ in range(duration):
            cpu_times = psutil.cpu_times_percent(interval=1)
            cpu_usage.append(psutil.cpu_percent(interval=0))
            mem_usage.append(psutil.virtual_memory().percent)
            context_switches.append(psutil.cpu_stats().ctx_switches)
            iowait.append(cpu_times.iowait)
        
        avg_cpu_usage = np.mean(cpu_usage)
        avg_mem_usage = np.mean(mem_usage)
        avg_context_switches = np.mean(context_switches)
        avg_iowait = np.mean(iowait)

        return avg_cpu_usage, avg_mem_usage, avg_context_switches, avg_iowait
