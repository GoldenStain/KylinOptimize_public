import pandas as pd
import numpy as np
from program.analysis.utils import identify,probability_bottleneck_result

if __name__ == "__main__":
    data = pd.read_csv('program/analysis/tests/testdata.csv')
    
    # 调用 identify 函数
    app_confidences = identify(data)
    resultdf = probability_bottleneck_result(data)
    print(app_confidences)
    print(resultdf)