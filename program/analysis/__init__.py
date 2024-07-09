import joblib
import os
import subprocess
import re

data_features = ['CPU.STAT.usr', 'CPU.STAT.nice', 'CPU.STAT.sys', 'CPU.STAT.iowait',
                              'CPU.STAT.irq', 'CPU.STAT.soft', 'CPU.STAT.steal', 'CPU.STAT.guest',
                              'CPU.STAT.util', 'CPU.STAT.cutil', 'STORAGE.STAT.rs',
                              'STORAGE.STAT.ws', 'STORAGE.STAT.rMBs', 'STORAGE.STAT.wMBs',
                              'STORAGE.STAT.rrqm', 'STORAGE.STAT.wrqm', 'STORAGE.STAT.rareq-sz',
                              'STORAGE.STAT.wareq-sz', 'STORAGE.STAT.r_await',
                              'STORAGE.STAT.w_await', 'STORAGE.STAT.util', 'STORAGE.STAT.aqu-sz',
                              'NET.STAT.rxkBs', 'NET.STAT.txkBs', 'NET.STAT.rxpcks',
                              'NET.STAT.txpcks', 'NET.STAT.ifutil', 'NET.ESTAT.errs',
                              'NET.ESTAT.util', 'MEM.MEMINFO.MemTotal', 'MEM.MEMINFO.MemFree',
                              'MEM.MEMINFO.MemAvailable','MEM.MEMINFO.SwapTotal','MEM.MEMINFO.Dirty',
                              'MEM.BANDWIDTH.Total_Util','PERF.STAT.IPC',
                              'PERF.STAT.CACHE-MISS-RATIO', 'PERF.STAT.MPKI',
                              'PERF.STAT.ITLB-LOAD-MISS-RATIO', 'PERF.STAT.DTLB-LOAD-MISS-RATIO',
                              'PERF.STAT.SBPI', 'PERF.STAT.SBPC', 'MEM.VMSTAT.procs.b','MEM.VMSTAT.memory.swpd',
                              'MEM.VMSTAT.io.bo', 'MEM.VMSTAT.system.in', 'MEM.VMSTAT.system.cs',
                              'MEM.VMSTAT.util.swap', 'MEM.VMSTAT.util.cpu', 'MEM.VMSTAT.procs.r',
                              'SYS.TASKS.procs', 'SYS.TASKS.cswchs', 'SYS.LDAVG.runq-sz',
                              'SYS.LDAVG.plist-sz', 'SYS.LDAVG.ldavg-1', 'SYS.LDAVG.ldavg-5',
                              'SYS.FDUTIL.fd-util']
perf_indicator = ['PERF.STAT.IPC', 'PERF.STAT.CACHE-MISS-RATIO', 'PERF.STAT.MPKI',
                        'PERF.STAT.ITLB-LOAD-MISS-RATIO', 'PERF.STAT.DTLB-LOAD-MISS-RATIO',
                        'PERF.STAT.SBPI', 'PERF.STAT.SBPC', ]

def consider_perf_detection():
    output = subprocess.check_output("perf stat -a -e cycles --interval-print 1000 --interval-count 1".split(),
                                        stderr=subprocess.STDOUT)
    event = 'cycles'
    pattern = r"^\ {2,}(\d.*?)\ {2,}(\d.*?)\ {2,}(\w*)\ {2,}(" + event + r")\ {1,}.*"
    search_obj = re.search(pattern, output.decode(), re.UNICODE | re.MULTILINE)
    if search_obj is None:
        return False
    return True

consider_perf = consider_perf_detection()


def get_consider_perf(consider_perf):
    if not consider_perf:
        features = [item for item in data_features if item not in perf_indicator]
    else:
        features = data_features
    return features


# 加载模型
model_path = "./program/analysis/models"
tencoder_path = os.path.join(model_path, "tencoder.pkl")
aencoder_path = os.path.join(model_path, "aencoder.pkl")
scaler_path = os.path.join(model_path, "scaler.pkl")
app_model_path = os.path.join(model_path, 'app_rf_clf.m')
app_feature_path = os.path.join(model_path, "app_feature.m")

scaler = joblib.load(scaler_path)
tencoder = joblib.load(tencoder_path)
aencoder = joblib.load(aencoder_path)
app_model_clf = joblib.load(app_model_path)
app_model_feat = joblib.load(app_feature_path)


