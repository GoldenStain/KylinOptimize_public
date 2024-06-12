import os
import sys

def gen_cpu_flame_graph(out_name, freq, pid=[]):
	pid_s = '' if len(pid) == 0 else '-p ' + ','.join(pid)
	os.system(f"python3.7m ebpf/BCCSource/tools/profile.py -af 10 {pid_s} > {out_name}.stacks01")
	os.system(f"./ebpf/FlameGraph/flamegraph.pl --color=java < {out_name}.stacks01 > {out_name}.svg")

if __name__ == '__main__':
	gen_cpu_flame_graph("out", 30, [])
	
