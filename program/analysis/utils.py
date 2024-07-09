import collections
from . import app_model_feat,app_model_clf,aencoder,scaler,get_consider_perf


def identify(data, consider_perf=True, get_consider_perf_func=get_consider_perf, 
             scaler=scaler, aencoder=aencoder, app_model_clf=app_model_clf, app_model_feat=app_model_feat, feature_selection=True, model='rf'):
    # 获取考虑的性能特征
    data_features = get_consider_perf_func(consider_perf)
    
    # 筛选数据特征
    data = data[data_features]
    
    # 数据预处理
    data = scaler.transform(data)

    # 特征选择
    if feature_selection and app_model_feat:
        app_data = app_model_feat.transform(data)
    else:
        app_data = data
    
    # 预测
    app_result = app_model_clf.predict(app_data)
    app_result = aencoder.inverse_transform(app_result)
    
    # 统计每个应用限制的出现次数
    app_counts = collections.Counter(app_result)
    
    # 计算每个应用限制的置信度
    app_confidences = {app: count / len(app_result) for app, count in app_counts.items()}
    
    return app_confidences



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