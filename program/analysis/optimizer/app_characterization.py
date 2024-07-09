"""
This class is used to train models and characterize system workload and application types.
"""

import os
import glob
import collections
import numpy as np
import pandas as pd
import joblib
import subprocess
import re
from sklearn.linear_model import Lasso
from sklearn.feature_selection import SelectFromModel
from sklearn.metrics import recall_score
from sklearn.model_selection import train_test_split as tts
from sklearn.metrics import accuracy_score
from analysis.optimizer.workload_characterization import WorkloadCharacterization
from analysis.optimizer.bottleneck_characterization import BottleneckCharacterization
from analysis.optimizer.deepforest import CascadeForestClassifier
import logging

import warnings
from sklearn.exceptions import UndefinedMetricWarning

# 设置日志记录器的配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
warnings.filterwarnings("ignore", category=UndefinedMetricWarning)

LOGGER = logging.getLogger(__name__)


class AppCharacterization(WorkloadCharacterization):
    """train models and characterize application"""

    def __init__(self, model_path, mode="all"):
        super().__init__(model_path)

        self.perf_indicator = ['PERF.STAT.IPC', 'PERF.STAT.CACHE-MISS-RATIO', 'PERF.STAT.MPKI',
                        'PERF.STAT.ITLB-LOAD-MISS-RATIO', 'PERF.STAT.DTLB-LOAD-MISS-RATIO',
                        'PERF.STAT.SBPI', 'PERF.STAT.SBPC', ]

        self.consider_perf = self.consider_perf_detection()

        if mode == "all":
            self.bottleneck = BottleneckCharacterization()

    def consider_perf_detection(self):
        output = subprocess.check_output("perf stat -a -e cycles --interval-print 1000 --interval-count 1".split(),
                                         stderr=subprocess.STDOUT)
        event = 'cycles'
        pattern = r"^\ {2,}(\d.*?)\ {2,}(\d.*?)\ {2,}(\w*)\ {2,}(" + event + r")\ {1,}.*"
        search_obj = re.search(pattern, output.decode(), re.UNICODE | re.MULTILINE)
        if search_obj is None:
            return False
        return True

    def parsing(self, data_path, data_features, header=0, analysis=False):
        """
        parse the data from csv
        :param data_path:  the path of csv
        """
        df_content = []
        csvfiles = glob.glob(data_path)
        selected_cols = list(data_features)
        selected_cols.append('workload.appname')

        for csv in csvfiles:
            data = pd.read_csv(csv, index_col=None, header=header, usecols=selected_cols)
            data[data_features] = self.abnormal_detection(data[data_features])
            df_content.append(data.dropna(axis=0))
        self.dataset = pd.concat(df_content, sort=False)
        if analysis:
            status_content = []
            for app, group in self.dataset.groupby('workload.appname'):
                status = group.describe()
                status['index'] = app
                status_content.append(status)
                total_status = pd.concat(status_content, sort=False)
            total_status.to_csv('statistics.csv')

    def feature_selection(self, x_axis, y_axis, data_features, clfpath=None):
        """
        feature selection for classifiers
        :param x_axis, y_axis:  orginal input and output data
        :returns selected_x:  selected input data
        """
        lasso = Lasso(alpha=0.01,max_iter=1000000).fit(x_axis, y_axis)
        importance = lasso.coef_.tolist()
        featureimportance = sorted(zip(data_features, importance), key=lambda x: -np.abs(x[1]))
        result = ", ".join(f"{label}: {round(coef, 3)}" for label, coef in featureimportance)
        LOGGER.info('Feature selection result of current classifier: %s', result)

        # Store selected column names into a list and return it as output
        self.selected_columns = [feat[0] for feat in featureimportance if abs(feat[1]) > 0.001]
        LOGGER.info('selected_columns: %s', self.selected_columns)
        
        feature_model = SelectFromModel(lasso, threshold=0.001)
        selected_x = feature_model.fit_transform(x_axis, y_axis)

        if clfpath is not None:
            joblib.dump(feature_model, clfpath)
        return selected_x


    def get_consider_perf(self, consider_perf):
        if not consider_perf:
            data_features = [item for item in self.data_features if item not in self.perf_indicator]
        else:
            data_features = self.data_features
        return data_features

    def train(self, data_path, feature_selection=False, search=False, model='rf', consider_perf=None):
        """
        train the data from csv
        :param data_path:  the data path
        :param model: training model, currently supports rf, deep-rf, svm and xgboost
        :param feature_selection:  whether to perform feature extraction
        :param search: whether to perform hyperparameter search
        :param consider_perf: whether to consider perf indicators
        """
        if consider_perf is None:
            consider_perf = self.consider_perf

        data_features = self.get_consider_perf(consider_perf)

        tencoder_path = os.path.join(self.model_path, "tencoder.pkl")
        aencoder_path = os.path.join(self.model_path, "aencoder.pkl")
        scaler_path = os.path.join(self.model_path, "scaler.pkl")
        data_path = os.path.join(data_path, "*.csv")
        
        app_model_clf = os.path.join(self.model_path, 'app_' + model + "_clf.m")
        app_feature = os.path.join(self.model_path, "app_feature.m")

        self.parsing(data_path, data_features)
        
        x = self.dataset.iloc[:, :-1]
        self.scaler.fit_transform(x)
        x = self.scaler.transform(x)

        app_y = self.aencoder.fit_transform(self.dataset.iloc[:, -1])

        joblib.dump(self.tencoder, tencoder_path)
        joblib.dump(self.aencoder, aencoder_path)
        joblib.dump(self.scaler, scaler_path)
        
        if feature_selection:
            app_x = self.feature_selection(x, app_y, data_features, app_feature)
        else:
            app_x = x


        if model == 'rf':
            LOGGER.info('app model start training')
            self.rf_clf(app_x, app_y, clfpath=app_model_clf, search=search)
        elif model == 'svm':
            LOGGER.info('app model start training')
            self.svm_clf(app_x, app_y, clfpath=app_model_clf, search=search)
        elif model == 'xgb':
            LOGGER.info('app model start training')
            self.xgb_clf(app_x, app_y, clfpath=app_model_clf)
        LOGGER.info('The overall classifier has been generated.')

    def identify(self, data, feature_selection=True, model='drf', consider_perf=None):
        """
        identify the workload_type according to input data
        :param model:
        :param data:  input data
        :param feature_selection:  whether to perform feature extraction
        :param consider_perf: whether to consider perf indicators
        """
        if consider_perf == None:
            consider_perf = self.consider_perf
            
        data_features = self.get_consider_perf(consider_perf)
        
        bottleneck_results_df = self.bottleneck.probability_bottleneck_result(data)
        
        data = data[data_features]
        LOGGER.info("Data before scaling:")
        LOGGER.info(data)  # Log the data before scaling
        
        tencoder_path = os.path.join(self.model_path, "tencoder.pkl")
        aencoder_path = os.path.join(self.model_path, "aencoder.pkl")
        scaler_path = os.path.join(self.model_path, "scaler.pkl")

        app_model_path = os.path.join(self.model_path, 'app_' + model + "_clf.m")
        LOGGER.info(f"Loading app model from: {app_model_path}")

        self.scaler = joblib.load(scaler_path)
        self.tencoder = joblib.load(tencoder_path)
        self.aencoder = joblib.load(aencoder_path)

        app_model_clf = joblib.load(app_model_path)

        LOGGER.info("Data before scaling:")
        LOGGER.info(data)  # 输入数据处理前的状态
        data = self.scaler.transform(data)
        LOGGER.info("Data after scaling:")
        LOGGER.info(data)  # 输入数据经过缩放后的值

        if feature_selection:
            app_feature = os.path.join(self.model_path, "app_feature.m")
            app_model_feat = joblib.load(app_feature)
            app_data = app_model_feat.transform(data)
        else:
            app_data = data
        
        app_result = app_model_clf.predict(app_data)
        app_result = self.aencoder.inverse_transform(app_result)
        LOGGER.info(f"App prediction result: {app_result}")
        
        app_prediction = collections.Counter(app_result).most_common(1)[0]
        LOGGER.info("App prediction: %s", app_prediction[0])
        
        app_confidence = app_prediction[1] / len(app_result) 
        
        
        if app_confidence < 0.5:
            applimit = 'default'
        else:
            applimit = app_prediction[0]
        
        # 瓶颈输出结果
        print(bottleneck_results_df)
        bottleneck_results_df.to_csv("bottleneck_results.csv")
        LOGGER.info("App limit prediction: %s with confidence %.2f", applimit, app_confidence)
        return  applimit, app_confidence