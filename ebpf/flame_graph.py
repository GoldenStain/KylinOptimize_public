import os
import sys

def gen_cpu_flame_graph(out_name, freq=30):
	os.system(f"python3.7m ebpf/BCCSource/tools/profile.py -af 10 > {out_name}.stacks01")
	os.system(f"./ebpf/FlameGraph/flamegraph.pl --color=java < {out_name}.stacks01 > {out_name}.svg")

if __name__ == '__main__':
	gen_cpu_flame_graph("out", 30)
	
