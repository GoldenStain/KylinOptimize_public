# encoding=utf-8
import time
from bcc import BPF, PerfType, PerfHWConfig
from ..server import globals
import psutil
from collections import defaultdict
import os

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

def init_ebpf(freq=49):
    bpf = BPF(src_file="program/ebpf/data_sample.c", cflags=[])

    bpf.attach_kprobe(event="tcp_sendmsg", fn_name="trace_tcp_sendmsg")
    bpf.attach_kprobe(event="tcp_recvmsg", fn_name="trace_tcp_recvmsg")
    bpf.attach_kprobe(event="blk_account_io_start", fn_name="trace_block_rq_insert")
    bpf.attach_kprobe(event="blk_mq_complete_request", fn_name="trace_disk_read")
    bpf.attach_kprobe(event="finish_task_switch", fn_name="kprobe__finish_task_switch")

    #bpf.attach_perf_event(ev_type=PerfType.HARDWARE, ev_config=PerfHWConfig.CPU_CYCLES, fn_name="trace_hw_cpu_cycles", sample_freq=freq, cpu=0)
    #bpf.attach_perf_event(ev_type=PerfType.HARDWARE, ev_config=PerfHWConfig.INSTRUCTIONS, fn_name="trace_ipc", sample_freq=freq)
    #bpf.attach_perf_event(ev_type=PerfType.HARDWARE, ev_config=PerfHWConfig.CACHE_REFERENCES, fn_name="trace_cache_hits", sample_freq=freq)
    #bpf.attach_perf_event(ev_type=PerfType.HARDWARE, ev_config=PerfHWConfig.CACHE_MISSES, fn_name="trace_cache_misses", sample_freq=freq)
    #bpf.attach_perf_event(ev_type=PerfType.HARDWARE, ev_config=PerfHWConfig.BRANCH_INSTRUCTIONS, fn_name="trace_branch_total", sample_freq=freq)
    #bpf.attach_perf_event(ev_type=PerfType.HARDWARE, ev_config=PerfHWConfig.BRANCH_MISSES, fn_name="trace_branch_misses", sample_freq=freq)

    return bpf

def get_dicts(bpf):
    dict_name = ["sent_bytes", "recv_bytes", "sent_count", "recv_count", "disk_read_bytes", "disk_write_bytes", "disk_read_count", "disk_write_count"
                , "cpu_usage", "disk_read_wait", "disk_write_wait", "mem_usage", "task_nvcsw", "task_nivcsw"
                #, "perf_hw_ipc", "perf_hw_cpu_cycles", "perf_cache_hits", "perf_cache_misses", "perf_branch_total", "perf_branch_misses"
                ]
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
    
    # 获取vmstat信息
    vmstat = os.popen("vmstat 1 1").readlines()
    vmstat = vmstat[2].split()
    # r: 运行队列的进程数
    # b: 等待IO的进程数
    # swpd: 虚拟内存已使用大小
    # free: 空闲内存大小
    # buff: 缓冲区内存大小
    # cache: 缓存内存大小
    # si: 从磁盘读入的内存大小
    # so: 从内存写入磁盘的内存大小
    # bi: 从磁盘读入的块数
    # bo: 从内存写入磁盘的块数
    # in: 每秒的中断数
    # cs: 每秒的上下文切换数
    # us: 用户空间占用CPU百分比
    # sy: 内核空间占用CPU百分比
    # id: 空闲CPU百分比
    # wa: 等待IO占用CPU百分比
    # st: 虚拟机偷取CPU时间百分比
    tags = ["r", "b", "swpd", "free", "buff", "cache", "si", "so", "bi", "bo", "in", "cs", "us", "sy", "id", "wa", "st"]
    for i in range(len(tags)):
        sum["vmstat_" + tags[i]] = int(vmstat[i])

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
    pid_dict = defaultdict(lambda: create_default(dicts))
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

    t = time.time()

    while True:
        delta_time = time.time() - t
        if delta_time < 1.0:
            time.sleep(1.0 - delta_time)
        t = time.time()

        pid_dict = get_proc_sum(dict_data)
        globals.SYSTEM_INFO = get_sum(dict_data)

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
            
        