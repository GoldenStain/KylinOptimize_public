import pandas as pd
import os
import sys
import joblib


FILE_PATH = os.path.realpath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(FILE_PATH, '..', '..'))

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)
    
from analysis.optimizer.app_characterization import AppCharacterization

# 初始化引擎配置
from analysis.engine.config import EngineConfig
config_file = '/home/wsw/桌面/KylinDBOptimize/analysis/engine/config.ini'
if EngineConfig.initial_params(config_file):
    print("Engine configuration initialized successfully.")
else:
    print("Failed to initialize engine configuration.")

# 创建 `AppCharacteristics` 类的实例
app_char = AppCharacterization('/home/wsw/桌面/KylinDBOptimize/analysis/models')

# 准备数据，确保数据是一个 DataFrame，包含所需特征
data = pd.read_csv('/home/wsw/桌面/KylinDBOptimize/analysis/tests/testdata.csv')


# 调用 identify 函数
applimit, app_confidence = app_char.identify(data, feature_selection=True, model='rf',consider_perf=True)

