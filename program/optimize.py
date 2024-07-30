#调优策略文件
import subprocess
from bcc import BPF, BPFProgType
from . import TuningManager
from .tools.numad import NumadManager

NUMA = None
def set_numa(flag):
    global NUMA
    if flag and NUMA is None:
        NUMA = NumadManager()
        NUMA.start_numad()
    elif not flag and not (NUMA is None):
        NUMA.stop_numad()
        NUMA = None

def get_numa():
    global NUMA
    return not (EBPF_LOOPBACK is None)

EBPF_LOOPBACK = None
def set_ebpf_loopback(flag):
    global EBPF_LOOPBACK
    if flag and EBPF_LOOPBACK is None:
        EBPF_LOOPBACK = BPF(src_file="program/ebpf/bpf_sockmap.c")
        EBPF_LOOPBACK.load_func("sock_ops_prog", BPFProgType.SOCK_OPS)
    elif not flag:
        EBPF_LOOPBACK = None

def get_ebpf_loopback():
    global EBPF_LOOPBACK
    return not (EBPF_LOOPBACK is None)


TUNING_ONLINE = None
def set_tuning_online(flag):
    global TUNING_ONLINE
    if flag and TUNING_ONLINE is None:
        try:
            subprocess.run(["sudo", "atune-adm", "analysis"], check=True)
            TUNING_ONLINE = True
        except subprocess.CalledProcessError as e:
            TUNING_ONLINE = None
        except Exception as e:
            TUNING_ONLINE = None
    elif not flag:
        TUNING_ONLINE = None
        
def get_tuning_online():
    return not (TUNING_ONLINE is None)


tuning_memory = TuningManager("stream","program/examples/tuning/memory/tuning_stream_client.yaml","program/tuning_log/tuning_memory.log")
def set_memory(flag):
    if flag == 0:
        pass
    elif flag == 1:
        tuning_memory.set_tuning()
    elif flag == 2:
        tuning_memory.restore_environment()


def get_memory():
    return tuning_memory.get_tuning_result()

tuning_mysql = TuningManager("mysql_sysbench","program/examples/tuning/mysql_sysbench/mysql_sysbench_client.yaml","program/tuning_log/tuning_mysql.log")
def set_mysql(flag):
    if flag == 0:
        pass
    elif flag == 1:
        tuning_mysql.set_tuning()
    elif flag == 2:
        tuning_mysql.restore_environment()


def get_mysql():
    return tuning_mysql.get_tuning_result()


# 一个bool数组
def set_policy_flags(arr):
    set_numa(arr[0])
    set_ebpf_loopback(arr[1])
    set_tuning_online(arr[2])
    set_memory(arr[3])
    set_mysql(arr[4])

def get_policy_flags():
    arr = []
    arr.append(get_numa())
    arr.append(get_ebpf_loopback())
    arr.append(get_tuning_online())
    arr.append(get_memory())
    arr.append(get_mysql())
    return arr
