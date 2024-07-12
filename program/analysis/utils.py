import collections
import torch
from . import app_char,NeuralNetwork,data_features


def identify(data, data_features=data_features, scaler=app_char.scaler,
              aencoder=app_char.aencoder, app_model_feat=app_char.app_model_feat,
              feature_selection=True,dict_param=app_char.dict_param):
    # 筛选数据特征
    data = data[data_features]
    
    # 数据预处理
    data = scaler.transform(data)

    # 特征选择
    if feature_selection and app_model_feat:
        app_data = app_model_feat.transform(data)
    else:
        app_data = data
    
    input_size = app_data.shape[1]
    neural_network = NeuralNetwork(input_size=input_size, hidden_size=64, output_size=7)
    neural_network.load_state_dict(dict_param)
    neural_network.eval()
    # 预测
    app_data_tensor = torch.tensor(app_data, dtype=torch.float32)
    with torch.no_grad():
        app_result = neural_network(app_data_tensor)

    # 返回每个应用限制的置信度
    return app_result.tolist()


import pandas as pd
import numpy as np
from . import BottleneckCharacterization

def probability_bottleneck_result(data):
        # 存储每行数据的概率结果
        bottleneck = BottleneckCharacterization()
        results = []
        # 遍历每行数据
        for index, row in data.iterrows():
            # 将每行数据转换为字典格式，传递给 probability_bottleneck 方法
            row_dict = row.to_dict()
            # 数据预处理
            preprocessed_data = bottleneck.preprocess_data(row_dict)
            probabilities = bottleneck.probability_bottleneck(preprocessed_data)
            results.append(probabilities)

        # 将结果转换为 DataFrame
        results_df = pd.DataFrame(results, columns=['CPU Prob', 'Memory Prob', 'Net Quality Prob', 'Net I/O Prob', 'Disk I/O Prob'])
         # 数据规范化
        normalized_results_df = bottleneck.normalize_data(results_df)
        
        return normalized_results_df

