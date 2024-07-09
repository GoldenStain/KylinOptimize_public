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
config_file = os.path.join(os.path.dirname(__file__), "../engine/config.ini")

if EngineConfig.initial_params(config_file):
    print("Engine configuration initialized successfully.")
else:
    print("Failed to initialize engine configuration.")

model_path = os.path.join(os.path.dirname(__file__), "../models")
# 创建 `AppCharacteristics` 类的实例
app_char = AppCharacterization(model_path)

model_path = os.path.join(os.path.dirname(__file__), "../tests/testdata.csv")
# 准备数据，确保数据是一个 DataFrame，包含所需特征
data = pd.read_csv(model_path)


# 调用 identify 函数
applimit, app_confidence = app_char.identify(data, feature_selection=True, model='rf',consider_perf=True)

