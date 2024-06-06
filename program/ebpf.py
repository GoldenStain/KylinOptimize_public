# encoding=utf-8
from bcc import BPF

with open("ebpf.c", "r") as f:
	prog = f.read()

bpf = BPF(text=prog)
bpf.trace_print()

