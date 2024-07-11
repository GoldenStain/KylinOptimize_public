#!/bin/bash


# 获取当前脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
echo "Script directory: $SCRIPT_DIR"
# 指定CSV数据文件的路径，相对于当前脚本的上级目录的analysis目录
CSV_PATH="$SCRIPT_DIR/../dataset"
echo "CSV path: $CSV_PATH"
# 指定模型保存路径，相对于当前脚本的上级目录的analysis目录
MODEL_PATH="$SCRIPT_DIR/../models"
echo "Model path: $MODEL_PATH"
# 是否进行特征选择
FEATURE_SELECTION="True"

# 是否启用参数空间搜索
SEARCH="True"

TYPE="nn"

# 运行Python脚本
python3 generate_models.py -d $CSV_PATH -m $MODEL_PATH -s $FEATURE_SELECTION -g $SEARCH -t $TYPE

