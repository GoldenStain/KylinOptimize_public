"""
This class is used to train models and characterize system workload.
"""

import os
import glob
import collections
import numpy as np
import pandas as pd
import joblib
from sklearn import svm
from sklearn.linear_model import Lasso
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectFromModel
from sklearn.model_selection import train_test_split as tts
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.utils import class_weight
from sklearn.model_selection import GridSearchCV


class WorkloadCharacterization:
    """train models and characterize system workload"""

    def __init__(self, model_path):
        self.model_path = model_path
        self.scaler = StandardScaler()
        self.tencoder = LabelEncoder()
        self.aencoder = LabelEncoder()
        self.dataset = None
        self.data_features = ['cpu_usage', 'disk_read_bytes', 'disk_write_bytes',
                              'disk_read_count', 'disk_write_count', 'disk_read_wait',
                              'disk_write_wait', 'mem_usage', 'task_nvcsw', 'task_nivcsw',
                              'sent_bytes', 'recv_bytes', 'sent_count', 'recv_count']

    @staticmethod
    def abnormal_detection(x_axis):
        """
        detect abnormal data points
        :param x_axis: the input data
        :returns result: filtered data
        """
        bool_normal = (x_axis.mean() - 3 * x_axis.std() <= x_axis) & \
                      (x_axis <= x_axis.mean() + 3 * x_axis.std())
        result = x_axis[bool_normal]
        return result

    def parsing(self, data_path, header=0, analysis=False):
        """
        parse the data from csv
        :param data_path:  the path of csv
        """
        df_content = []  # 用于存储每个CSV文件解析后的数据帧列表
        csvfiles = glob.glob(data_path)  # 获取指定路径下所有符合条件的CSV文件列表
        selected_cols = list(self.data_features)  # 从对象中获取数据特征列表
        selected_cols.append('workload.type')  # 添加 'workload.type' 到选定列列表
        selected_cols.append('workload.appname')  # 添加 'workload.appname' 到选定列列表

        for csv in csvfiles:
            data = pd.read_csv(csv, index_col=None, header=header, usecols=selected_cols)
            data[self.data_features] = self.abnormal_detection(data[self.data_features])

            # 删除含有NaN值的行，并将处理后的数据帧添加到列表中
            df_content.append(data.dropna(axis=0))
            # 将所有处理后的数据帧合并为一个数据集
        self.dataset = pd.concat(df_content, sort=False)
        if analysis:
            status_content = []  # 用于存储每个应用程序统计信息的列表
            for app, group in self.dataset.groupby('workload.appname'):
                status = group.describe()
                status['index'] = app
                status_content.append(status)

            # 将所有应用程序的统计信息合并为一个数据帧，并保存为CSV文件
            total_status = pd.concat(status_content, sort=False)
            total_status.to_csv('statistics.csv')

    def feature_selection(self, x_axis, y_axis, clfpath=None):
        """
        feature selection for classifiers
        :param x_axis, y_axis:  orginal input and output data
        :returns selected_x:  selected input data
        """
        #  alpha=0.01 是Lasso回归的超参数，控制稀疏性。
        lasso = Lasso(alpha=0.01).fit(x_axis, y_axis)
        # 获取每个特征的系数（重要性）并转换为列表格式。
        importance = lasso.coef_.tolist()
        # 将特征名称与其重要性系数进行排序，按照绝对值降序排列。
        featureimportance = sorted(zip(self.data_features, importance), key=lambda x: -np.abs(x[1]))
        result = ", ".join(f"{label}: {round(coef, 3)}" for label, coef in featureimportance)
        print("Feature selection result of current classifier:", result)

        feature_model = SelectFromModel(lasso, threshold=0.001)
        selected_x = feature_model.fit_transform(x_axis, y_axis)
        if clfpath is not None:
            joblib.dump(feature_model, clfpath)
        return selected_x

    @staticmethod
    def svm_clf(x_axis, y_axis, clfpath=None, kernel='rbf', search=False):
        """
        svm_clf: support vector machine classifier
        """
        x_train, x_test, y_train, y_test = tts(x_axis, y_axis, test_size=0.3)
        model = svm.SVC(kernel=kernel, C=100, class_weight='balanced', gamma='auto')
        if search:
            tuned_parameters = [
                {'C': range(10, 200, 20), 'kernel': ['poly'],
                 'degree': range(1, 10, 2), 'gamma': ['scale', 'auto']},
                {'C': range(10, 200, 20), 'kernel': ['rbf'],
                 'gamma': ['scale', 'auto']},
                {'C': range(10, 200, 20), 'kernel': ['sigmoid'],
                 'gamma': ['scale', 'auto']},
            ]
            # 用网格搜索交叉验证（Grid Search CV），寻找最佳的模型参数组合。
            model = GridSearchCV(estimator=model, param_grid=tuned_parameters,
                                 cv=5, n_jobs=-1, pre_dispatch='0.5*n_jobs')
        model.fit(x_train, y_train)
        y_pred = model.predict(x_test)
        print(f"the accuracy of svc classifier is {accuracy_score(y_test, y_pred)}")
        if hasattr(model, 'best_params_'):
            print(f"the grid search best params is: {model.best_params_}")
        if clfpath is not None:
            joblib.dump(model, clfpath)
        return model

    @staticmethod
    def rf_clf(x_axis, y_axis, clfpath=None, search=False):
        """
        ada_clf: Adaptive Boosting classifier
        """
        x_train, x_test, y_train, y_test = tts(x_axis, y_axis, test_size=0.3)
        model = RandomForestClassifier(n_estimators=150, class_weight='balanced',
                                       oob_score=True, random_state=0, n_jobs=-1)
        if search:
            tuned_parameters = {'n_estimators': range(100, 400, 50),
                                'criterion': ['gini', 'entropy'], 'max_features': ['sqrt', 'log2']}
            model = GridSearchCV(estimator=model, param_grid=tuned_parameters,
                                 cv=5, n_jobs=-1, pre_dispatch='0.5*n_jobs')
        model.fit(x_train, y_train)
        y_pred = model.predict(x_test)
        print(f"the accuracy of random forest classifier is {accuracy_score(y_test, y_pred)}")
        if hasattr(model, 'best_params_'):
            print(f"the grid search best params is: {model.best_params_}")
        if clfpath is not None:
            joblib.dump(model, clfpath)
        return model

    @staticmethod
    def xgb_clf(x_axis, y_axis, clfpath=None):
        """
        XGb_clf: XGBoost classifier
        """
        from xgboost import XGBClassifier
        x_train, x_test, y_train, y_test = tts(x_axis, y_axis, test_size=0.3)
        weights = list(
            class_weight.compute_class_weight(class_weight='balanced', classes=np.unique(y_train), y=y_train))
        class_weights = dict(zip(np.unique(y_train), weights))
        w_array = np.ones(y_train.shape[0], dtype='float')
        for i, val in enumerate(y_train):
            w_array[i] = class_weights[val]
        model = XGBClassifier(learning_rate=0.1, n_estimators=400, max_depth=6,
                              min_child_weight=0.5, gamma=0.01, subsample=1, colsample_btree=1,
                              scale_pos_weight=1, random_state=27, slient=0, alpha=100)
        model.fit(x_train, y_train, sample_weight=w_array)
        y_pred = model.predict(x_test)
        print(f"the accuracy of xgboost classifier is {accuracy_score(y_test, y_pred)}")
        if clfpath is not None:
            joblib.dump(model, clfpath)
        return model

    def train(self, data_path, feature_selection=False, search=False):
        """
        train the data from csv
        :param data_path:  the data path
        """
        tencoder_path = os.path.join(self.model_path, "tencoder.pkl")
        aencoder_path = os.path.join(self.model_path, "aencoder.pkl")
        scaler_path = os.path.join(self.model_path, "scaler.pkl")
        data_path = os.path.join(data_path, "*.csv")

        type_clf = os.path.join(self.model_path, "total_clf.m")
        type_feature = os.path.join(self.model_path, "total_feature.m")

        self.parsing(data_path)

        x_type = self.dataset.iloc[:, :-2].copy()  # 提取特征数据 x_type，排除最后两列（类型和应用名）。
        self.scaler.fit_transform(x_type)
        y_type = self.tencoder.fit_transform(self.dataset.iloc[:, -2])
        y_app = self.aencoder.fit_transform(self.dataset.iloc[:, -1])
        joblib.dump(self.tencoder, tencoder_path)
        joblib.dump(self.aencoder, aencoder_path)
        joblib.dump(self.scaler, scaler_path)

        if feature_selection:
            x_type = self.feature_selection(x_type, y_type, type_feature)
            x_type = self.scaler.transform(x_type)  # 特征选择后重新缩放

        self.rf_clf(x_type, y_type, clfpath=type_clf, search=search)
        print("The overall classifier has been generated.")

        for workload, group in self.dataset.groupby('workload.type'):
            x_app = self.scaler.transform(group.iloc[:, :-2].copy())
            y_app = self.aencoder.transform(group.iloc[:, -1])

            clf_name = workload + "_clf.m"
            feature_name = workload + "_feature.m"
            clf_path = os.path.join(self.model_path, clf_name)
            feature_path = os.path.join(self.model_path, feature_name)

            if feature_selection:
                x_app = self.feature_selection(x_app, y_app, feature_path)

            if workload == "default":
                self.rf_clf(x_app, y_app, clf_path, search=search)
            elif workload == "throughput_performance":
                self.svm_clf(x_app, y_app, clf_path, search=search)
            print("The application classifiers have been generated.")

    def identify(self, data, feature_selection=False):
        """
        identify the workload_type according to input data
        :param data:  input data
        """
        data = data[self.data_features]
        tencoder_path = os.path.join(self.model_path, "tencoder.pkl")
        aencoder_path = os.path.join(self.model_path, "aencoder.pkl")
        scaler_path = os.path.join(self.model_path, "scaler.pkl")

        type_path = os.path.join(self.model_path, "total_clf.m")
        df_path = os.path.join(self.model_path, "default_clf.m")
        tp_path = os.path.join(self.model_path, "throughput_performance_clf.m")

        self.scaler = joblib.load(scaler_path)
        self.tencoder = joblib.load(tencoder_path)
        self.aencoder = joblib.load(aencoder_path)

        type_clf = joblib.load(type_path)
        df_clf = joblib.load(df_path)
        tp_clf = joblib.load(tp_path)

        data = self.scaler.transform(data)

        if feature_selection:
            feature_path = os.path.join(self.model_path, "total_feature.m")
            df_feature = os.path.join(self.model_path, "default_feature.m")
            tp_feature = os.path.join(self.model_path, "throughput_performance_feature.m")

            type_feat = joblib.load(feature_path)
            df_feat = joblib.load(df_feature)
            tp_feat = joblib.load(tp_feature)

            df_data = df_feat.transform(data)
            tp_data = tp_feat.transform(data)
            data = type_feat.transform(data)
        workload = type_clf.predict(data)
        workload = self.tencoder.inverse_transform(workload)
        print("Current workload:", workload)
        prediction = collections.Counter(workload).most_common(1)[0]
        confidence = prediction[1] / len(workload)

        if confidence < 0.5:
            resourcelimit = 'default'
            return resourcelimit, "default", confidence

        if confidence < 0.5:
            resourcelimit = 'default'
            return resourcelimit, "default", confidence
        if prediction[0] == 'throughput_performance':
            resourcelimit = "throughput"
            if feature_selection:
                data = tp_data
            result = tp_clf.predict(data)
        else:
            resourcelimit = "default"
            if feature_selection:
                data = df_data
            result = df_clf.predict(data)
            result = df_clf.predict(data)

        result = self.aencoder.inverse_transform(result)
        print(result)
        prediction = collections.Counter(result).most_common(1)[0]
        confidence = prediction[1] / len(result)

        if confidence > 0.5:
            return resourcelimit, prediction[0], confidence

        return resourcelimit, "default", confidence

    def retrain(self, data_path, custom_path):
        """
        for user: train model according to the collecting data
        """
        custom_path = os.path.abspath(custom_path)
        (dirname, filename) = os.path.split(custom_path)
        (modelname, _) = os.path.splitext(filename)
        scalername = modelname + '_scaler.pkl'
        encodername = modelname + '_encoder.pkl'

        data_path = os.path.join(data_path, "*.csv")
        self.parsing(data_path)
        x_axis = self.scaler.fit_transform(self.dataset.iloc[:, :-2])
        y_axis = self.aencoder.fit_transform(self.dataset.iloc[:, -1])
        joblib.dump(self.scaler, os.path.join(dirname, scalername))
        joblib.dump(self.aencoder, os.path.join(dirname, encodername))

        class_num = len(self.aencoder.classes_)
        if class_num == 1:
            y_axis[-1] = y_axis[-1] + 1
        self.svm_clf(x_axis, y_axis, custom_path)

    def reidentify(self, data, custom_path):
        """
        for user: predict workload type
        """
        data = data[self.data_features]
        custom_path = os.path.abspath(custom_path)
        (dirname, filename) = os.path.split(custom_path)
        (modelname, _) = os.path.splitext(filename)
        scalername = modelname + '_scaler.pkl'
        encodername = modelname + '_encoder.pkl'

        scaler = joblib.load(os.path.join(dirname, scalername))
        encoder = joblib.load(os.path.join(dirname, encodername))
        model = joblib.load(custom_path)

        data = scaler.transform(data)
        result = model.predict(data)
        result = encoder.inverse_transform(result)
        print(result)

        prediction = collections.Counter(result).most_common(1)[0]
        confidence = prediction[1] / len(result)

        if confidence > 0.5:
            return prediction[0], confidence

        return "default", confidence
