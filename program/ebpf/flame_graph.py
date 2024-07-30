import os
import sys

def gen_cpu_flame_graph(out_name, freq=50, pid=[]):
	pid_s = '' if len(pid) == 0 else '-p ' + ','.join(pid)
	os.system(f"python3.7m program/ebpf/BCCSource/tools/profile.py -afd -F {freq} {pid_s} 10 > {out_name}.stacks01")
	os.system(f"./program/ebpf/FlameGraph/flamegraph.pl --color=java --bgcolors '#101070' < {out_name}.stacks01 > {out_name}.svg")
	os.system(f"sed -i '13s/rgb(0,0,0)/rgb(255,255,255)/' {out_name}.svg")

def gen_flame_graph_perf(out_name, freq=50, time=10, pid=[]):
	pid_s = '' if len(pid) == 0 else '-p ' + ','.join(pid)
	os.system(f"perf record --call-graph dwarf,32 -F {freq} -g -a {pid_s} -- sleep {time}")
	os.system(f"perf script -i perf.data > {out_name}.stacks01")
	os.system(f"./program/ebpf/FlameGraph/stackcollapse-perf.pl {out_name}.stacks01 > {out_name}.stacks02")
	os.system(f"./program/ebpf/FlameGraph/flamegraph.pl --color=java --bgcolors '#101070' < {out_name}.stacks02 > {out_name}.svg")
	os.system(f"sed -i '13s/rgb(0,0,0)/rgb(255,255,255)/' {out_name}.svg")

def gen_flame_graph_cmd(out_name, name, cmd, freq=50):
	line = f"perf record --call-graph dwarf,32 -F {freq} -g -p $(pgrep -x {name}) -- {cmd}"
	print(line)
	os.system(line)
	os.system(f"perf script -i perf.data > {out_name}.stacks01")
	os.system(f"./program/ebpf/FlameGraph/stackcollapse-perf.pl {out_name}.stacks01 > {out_name}.stacks02")
	os.system(f"./program/ebpf/FlameGraph/flamegraph.pl --color=java --bgcolors '#101070' < {out_name}.stacks02 > {out_name}.svg")
	os.system(f"sed -i '13s/rgb(0,0,0)/rgb(255,255,255)/' {out_name}.svg")

if __name__ == '__main__':
	gen_cpu_flame_graph("out", 30, [])
	# gen_flame_graph_perf("out")
	
