from analysis.engine.config import EngineConfig
import logging
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
LOGGER = logging.getLogger(__name__)

class BottleneckCharacterization:
        
    def __init__(self):
        self.cpu_thresholds = {
            'CPU.STAT.util': float(EngineConfig.cpu_stat_util), 
            'CPU.STAT.cutil': float(EngineConfig.cpu_stat_cutil), 
            'PERF.STAT.IPC': float(EngineConfig.perf_stat_ipc)
        }
        self.mem_thresholds = {
            'MEM.BANDWIDTH.Total_Util': float(EngineConfig.mem_bandwidth_total_util), 
            'MEM.VMSTAT.util.swap': float(EngineConfig.mem_vmstat_util_swap), 
            'MEM.VMSTAT.util.cpu': float(EngineConfig.mem_vmstat_util_cpu)
        }
        self.net_quality_thresholds = {
            'NET.STAT.ifutil': float(EngineConfig.net_stat_ifutil), 
            'NET.ESTAT.errs': float(EngineConfig.net_estat_errs)
        }
        self.net_io_thresholds = {
            'NET.STAT.rxkBs': float(EngineConfig.net_stat_rxkbs), 
            'NET.STAT.txkBs': float(EngineConfig.net_stat_txkbs)
        }
        self.disk_io_thresholds = {
            'STORAGE.STAT.util': float(EngineConfig.storage_stat_util)
        }
                
    def search_bottleneck(self, data):
        LOGGER.info("cpu_thresholds: %s", self.cpu_thresholds)
        LOGGER.info("mem_thresholds: %s", self.mem_thresholds)
        LOGGER.info("net_quality_thresholds: %s", self.net_quality_thresholds)
        LOGGER.info("net_io_thresholds: %s", self.net_io_thresholds)
        LOGGER.info("disk_io_thresholds: %s", self.disk_io_thresholds)
        
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
        
        LOGGER.info('The probability of %s bottleneck is: %s', bottleneck_type, average_probability)
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
        # 假设数据已经是 DataFrame 格式
        scaler = MinMaxScaler()
        normalized_data = scaler.fit_transform(data)
        return pd.DataFrame(normalized_data, columns=data.columns)
    
    
    
    def probability_bottleneck_result(self, data):
          # 存储每行数据的概率结果
        results = []
        # 遍历每行数据
        for index, row in data.iterrows():
            # 将每行数据转换为字典格式，传递给 probability_bottleneck 方法
            row_dict = row.to_dict()
            # 数据预处理
            preprocessed_data = self.preprocess_data(row_dict)
            probabilities = self.probability_bottleneck(preprocessed_data)
            results.append(probabilities)

        # 将结果转换为 DataFrame
        results_df = pd.DataFrame(results, columns=['CPU Prob', 'Memory Prob', 'Net Quality Prob', 'Net I/O Prob', 'Disk I/O Prob'])
         # 数据规范化
        normalized_results_df = self.normalize_data(results_df)
        return normalized_results_df
