import os
import sys
import numpy as np
import pandas as pd

FILE_PATH = os.path.realpath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(FILE_PATH, '..', '..'))

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# from analysis.optimizer.workload_characterization import WorkloadCharacterization
from analysis.optimizer.app_characterization import AppCharacterization

def main():
    model_path = "/home/wsw/桌面/KylinDBOptimize/analysis/models"
    data_path = "/home/wsw/桌面/KylinDBOptimize/analysis/tests/testdata.csv"
    consider_perf = True  # 根据需要设置是否考虑性能指标
    feature_selection = True  # 根据需要设置是否进行特征选择

    # 创建 AppCharacterization 实例
    app_char = AppCharacterization(model_path)

    # 读取数据
    data = pd.read_csv(data_path)

    # 检测模型
    bottleneck_binary, resourcelimit, applimit, app_confidence = app_char.identify(data, feature_selection=feature_selection, consider_perf=consider_perf)

    # 输出结果
    print("Bottleneck Binary:", bottleneck_binary)
    print("Resource Limit:", resourcelimit)
    print("Application Limit:", applimit)
    print("Application Confidence:", app_confidence)

if __name__ == "__main__":
    main()
