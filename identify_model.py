import pandas as pd
from program.analysis.utils import identify

if __name__ == "__main__":
    data = pd.read_csv('/home/wsw/桌面/KylinDBOptimize/program/analysis/tests/testdata.csv')

    # 调用 identify 函数
    app_confidences = identify(data)
    print(app_confidences)
