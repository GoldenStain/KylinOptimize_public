# 调优策略文件
from bcc import BPF, BPFProgType

NUMA = None
def set_numa(flag):
    pass

def get_numa():
    return False

EBPF_LOOPBACK = None
def set_ebpf_loopback(flag):
    if flag and EBPF_LOOPBACK is None:
        EBPF_LOOPBACK = BPF(src_file="program/ebpf/bpf_sockmap.c")
        EBPF_LOOPBACK.load_func("bpf_redir", BPFProgType.SK_MSG)
        EBPF_LOOPBACK.load_func("bpf_sockops_handler", BPFProgType.SOCK_OPS)
    elif not flag:
        EBPF_LOOPBACK = None

def get_ebpf_loopback():
    return not (EBPF_LOOPBACK is None)

# 一个bool数组
def set_policy_flags(arr):
    set_numa(arr[0])
    set_ebpf_loopback(arr[1])

def get_policy_flags():
    arr = []
    arr.append(get_numa())
    arr.append(get_ebpf_loopback())
    return arr