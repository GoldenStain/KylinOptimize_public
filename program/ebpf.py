#!/usr/bin/python
# encoding=utf-8

from bcc import BPF
import ctypes
import time

bpf = BPF(src_file="bpf_data.c")
bpf.attach_kprobe(event="tcp_sendmsg", fn_name="trace_tcp_sendmsg")
bpf.attach_kprobe(event="tcp_recvmsg", fn_name="trace_tcp_recvmsg")

send_bytes = bpf["send_bytes"]
recv_bytes = bpf["recv_bytes"]

while True:
	try:
		for k, v in send_bytes.items():
			sock = k.value
			bytes_sent = v.value
			print(f"Socket {hex(sock)} sent {bytes_sent} bytes")
		for k, v in recv_bytes.items():
			sock = k.value
			bytes_recv = v.value
			print(f"Socket {hex(sock)} received {bytes_recv} bytes")

		send_bytes.clear()
		recv_bytes.clear()

		time.sleep(0.1)
	except KeyboardInterrupt:
		exit()

