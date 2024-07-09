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

