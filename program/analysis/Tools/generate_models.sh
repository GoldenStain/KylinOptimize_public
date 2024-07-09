#!/bin/bash

# 指定CSV数据文件的路径
CSV_PATH="/home/wsw/桌面/KylinDBOptimize/analysis/dataset"

# 指定模型保存路径
MODEL_PATH="/home/wsw/桌面/KylinDBOptimize/analysis/models"

# 是否进行特征选择
FEATURE_SELECTION="True"

# 是否启用参数空间搜索
SEARCH="True"

TYPE="rf"

# 运行Python脚本
python3 generate_models.py -d $CSV_PATH -m $MODEL_PATH -s $FEATURE_SELECTION -g $SEARCH -t $TYPE

