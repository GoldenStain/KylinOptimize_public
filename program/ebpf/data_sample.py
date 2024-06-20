# encoding=utf-8
import time
from bcc import BPF
from ..server import globals
import psutil
from collections import defaultdict

def read_bpf_data(bpf, t_pid=0):
    send_bytes = bpf["send_bytes"]
    recv_bytes = bpf["recv_bytes"]

    disk_read_bytes = bpf["disk_read_bytes"]
    disk_write_bytes = bpf["disk_write_bytes"]
    disk_read_count = bpf["disk_read_count"]
    disk_write_count = bpf["disk_write_count"]

    cpu_usage = bpf["cpu_usage"]
    mem_usage = bpf["mem_usage"]

    TCP_sent = 0
    TCP_recv = 0
    DISK_read = 0
    DISK_write = 0
    DISK_read_cnt = 0
    DISK_write_cnt = 0
    CPU_usage = 0
    MEM_usage = 0

    for k, v in send_bytes.items():
        pid = k.value
        bytes_sent = v.value
        if t_pid == 0 or pid == t_pid:
            TCP_sent += bytes_sent
        #print(f"Process {pid} sent {bytes_sent} bytes")
    for k, v in recv_bytes.items():
        pid = k.value
        bytes_recv = v.value
        if t_pid == 0 or pid == t_pid:
            TCP_recv += bytes_recv
        #print(f"Process {pid} received {bytes_recv} bytes")
    
    for k, v, in disk_read_bytes.items():
        pid = k.value
        value = v.value
        if t_pid == 0 or pid == t_pid:
            DISK_read += value
    for k, v, in disk_write_bytes.items():
        pid = k.value
        value = v.value
        if t_pid == 0 or pid == t_pid:
            DISK_write += value
    for k, v, in disk_read_count.items():
        pid = k.value
        value = v.value
        if t_pid == 0 or pid == t_pid:
            DISK_read_cnt += value
    for k, v, in disk_write_count.items():
        pid = k.value
        value = v.value
        if t_pid == 0 or pid == t_pid:
            DISK_write_cnt += value
    
    for k, v, in cpu_usage.items():
        pid = k.value
        value = v.value
        if t_pid == 0 or pid == t_pid:
            CPU_usage += value
    CPU_usage /= 1e9

    # for k, v, in mem_usage.items():
    # 	pid = k.value
    # 	value = v.value
    # 	if t_pid == 0 or pid == t_pid:
    # 		MEM_usage += value

    send_bytes.clear()
    recv_bytes.clear()

    disk_read_bytes.clear()
    disk_write_bytes.clear()
    disk_read_count.clear()
    disk_write_count.clear()

    cpu_usage.clear()
    
    return {
        "TCP_sent": TCP_sent,
        "TCP_recv": TCP_recv,
        "DISK_read": DISK_read,
        "DISK_write": DISK_write,
        "DISK_read_cnt": DISK_read_cnt,
        "DISK_write_cnt": DISK_write_cnt,
        "CPU_usage": CPU_usage
    }

def init_ebpf():
    bpf = BPF(src_file="program/ebpf/data_sample.c")
    bpf.attach_kprobe(event="tcp_sendmsg", fn_name="trace_tcp_sendmsg")
    bpf.attach_kprobe(event="tcp_recvmsg", fn_name="trace_tcp_recvmsg")
    bpf.attach_kprobe(event="blk_account_io_start", fn_name="trace_block_rq_insert")
    bpf.attach_kprobe(event="blk_mq_complete_request", fn_name="trace_disk_read")
    bpf.attach_kprobe(event="finish_task_switch", fn_name="kprobe__finish_task_switch")
    return bpf

def get_dicts(bpf):
    dict_name = ["sent_bytes", "recv_bytes", "sent_count", "recv_count", "disk_read_bytes", "disk_write_bytes", "disk_read_count", "disk_write_count"
                 , "cpu_usage", "disk_read_wait", "disk_write_wait"]
    dict_data = {}
    for name in dict_name:
        dict_data[name] = bpf[name]
    return dict_data

def get_sum(dicts):
    sum = {}
    for name, data in dicts.items():
        sum[name] = 0.0
        for k, v in data.items():
            val = v.value
            sum[name] += val
    return sum

def create_default(dicts):
    d = {}
    for name in dicts:
        d[name] = 0.0
    return d

def get_pid_sum(dicts, t_pid):
    res = create_default()
    for name, data in dicts.items():
        for k, v in data.items():
            pid = str(k.value)
            if pid == t_pid:
                val = v.value
                res[name] = val
    return res

def get_proc_sum(dicts):
    pid_dict = defaultdict(create_default)
    for name, data in dicts.items():
        for k, v in data.items():
            pid = str(k.value)
            val = v.value
            pid_dict[pid][name] = val
    return pid_dict

def clear_dicts(bpf, dicts):
    for name, data in dicts.items():
        data.clear()
    bpf["start_times"].clear()

def start():
    bpf = init_ebpf()
    dict_data = get_dicts(bpf)
    while True:
        time.sleep(1.0)

        def create_default():
            d = {}
            for name in dict_data:
                d[name] = 0.0
            return d

        globals.SYSTEM_INFO = get_sum(dict_data)
        pid_dict = get_proc_sum(dict_data)

        temp = []
        for pid, data in pid_dict.items():
            p_dict = {}
            p_dict["pid"] = int(pid)

            try:
                p_dict["name"] = psutil.Process(int(pid)).name()
            except:
                continue

            for name in dict_data:
                p_dict[name] = data[name]
            temp.append(p_dict)
        
        clear_dicts(bpf, dict_data)
        
        temp.sort(key=lambda item: item["name"])

        globals.PROCESS_INFO = temp
            
        