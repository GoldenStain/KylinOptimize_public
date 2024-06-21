import os
import sys

def gen_cpu_flame_graph(out_name, freq=50, pid=[]):
	pid_s = '' if len(pid) == 0 else '-p ' + ','.join(pid)
	os.system(f"python3.7m program/ebpf/BCCSource/tools/profile.py -afd --stack-storage-size 2048 -F {freq} {pid_s} 10 > {out_name}.stacks01")
	os.system(f"./program/ebpf/FlameGraph/flamegraph.pl --color=java --bgcolors '#101070' < {out_name}.stacks01 > {out_name}.svg")

if __name__ == '__main__':
	gen_cpu_flame_graph("out", 30, [])
	
