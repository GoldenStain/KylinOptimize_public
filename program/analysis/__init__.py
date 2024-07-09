import joblib
import os
import subprocess
import re
import pandas as pd
import numpy as np

from sklearn.preprocessing import MinMaxScaler

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


class BottleneckCharacterization:
        
    def __init__(self):
        
        self.cpu_thresholds = {
            'CPU.STAT.util': float(80), 
            'CPU.STAT.cutil': float(80), 
            'PERF.STAT.IPC': float(1)
        }
        self.mem_thresholds = {
            'MEM.BANDWIDTH.Total_Util': float(70), 
            'MEM.VMSTAT.util.swap': float(70), 
            'MEM.VMSTAT.util.cpu': float(70)
        }
        self.net_quality_thresholds = {
            'NET.STAT.ifutil': float(70), 
            'NET.ESTAT.errs': float(1)
        }
        self.net_io_thresholds = {
            'NET.STAT.rxkBs': float(70), 
            'NET.STAT.txkBs': float(70)
        }
        self.disk_io_thresholds = {
            'STORAGE.STAT.util': float(70)
        }
                
    def search_bottleneck(self, data):
        
        cpu_probability = self.check_thresholds(data, self.cpu_thresholds, "computational", special_key='PERF.STAT.IPC', special_value=-1)
        mem_probability = self.check_thresholds(data, self.mem_thresholds, "memory")
        net_quality_probability = self.check_thresholds(data, self.net_quality_thresholds, "network quality")
        net_io_probability = self.check_thresholds(data, self.net_io_thresholds, "network I/O")
        disk_io_probability = self.check_thresholds(data, self.disk_io_thresholds, "disk I/O")
        
        return cpu_probability, mem_probability, net_quality_probability, net_io_probability, disk_io_probability
    
    def check_thresholds(self, data, thresholds, bottleneck_type, special_key=None, special_value=None):
        probabilities=[]
        for key, threshold in thresholds.items():
            value = data.get(key)
            if value is None or pd.isna(value):
                probabilities.append(0)
                continue
           
            if special_key is not None and key == special_key and value != special_value and value < threshold:
                probability = 1 - value / threshold
                probabilities.append(probability)
            elif value >= threshold:
                percentage_over_threshold = (value - threshold) / threshold  # 超过阈值的百分比
                probability = min(1.0, 0.7 + 0.3 * percentage_over_threshold)  # 根据超过阈值的百分比调整概率
                probabilities.append(probability)
            else:
                percentage_of_threshold = value / threshold  # 未超过阈值的百分比
                probability = min(0.7, 0.3 + 0.4 * percentage_of_threshold)  # 根据未超过阈值的百分比调整概率
                probabilities.append(probability)
                
        if probabilities:
            average_probability = np.mean(probabilities)
        else:
            average_probability = 0
            
        return average_probability
    
    
    def probability_bottleneck(self,data):
        
        cpu_prob, mem_prob, net_quality_prob, net_io_prob, disk_io_prob = self.search_bottleneck(data)
        return [cpu_prob, mem_prob, net_quality_prob, net_io_prob, disk_io_prob]
    
    
    def preprocess_data(self, row_dict):
        # 去除异常值和处理缺失值（示例）
        cleaned_data = {}
        for key, value in row_dict.items():
            if value is None or pd.isna(value):
                cleaned_data[key] = 0  # 用0替换缺失值，或使用其他方法填补
            elif value < 0 or value > 1e6:  # 假设异常值范围
                cleaned_data[key] = 0  # 去除异常值，或使用其他方法处理
            else:
                cleaned_data[key] = value
        
        return cleaned_data

    def normalize_data(self, data):
        scaler = MinMaxScaler()
        normalized_data = scaler.fit_transform(data)
        return pd.DataFrame(normalized_data, columns=data.columns)
