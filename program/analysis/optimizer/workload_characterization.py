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
from sklearn.metrics import accuracy_score,confusion_matrix, classification_report, roc_curve, roc_auc_score
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
        self.data_features = ['CPU.STAT.usr', 'CPU.STAT.nice', 'CPU.STAT.sys', 'CPU.STAT.iowait',
                              'CPU.STAT.irq', 'CPU.STAT.soft', 'CPU.STAT.steal', 'CPU.STAT.guest',
                              'CPU.STAT.util', 'CPU.STAT.cutil', 'STORAGE.STAT.rs',
                              'STORAGE.STAT.ws', 'STORAGE.STAT.rMBs', 'STORAGE.STAT.wMBs',
                              'STORAGE.STAT.rrqm', 'STORAGE.STAT.wrqm', 'STORAGE.STAT.rareq-sz',
                              'STORAGE.STAT.wareq-sz', 'STORAGE.STAT.r_await',
                              'STORAGE.STAT.w_await', 'STORAGE.STAT.util', 'STORAGE.STAT.aqu-sz',
                              'NET.STAT.rxkBs', 'NET.STAT.txkBs', 'NET.STAT.rxpcks',
                              'NET.STAT.txpcks', 'NET.STAT.ifutil', 'NET.ESTAT.errs',
                              'NET.ESTAT.util', 'MEM.MEMINFO.MemTotal', 'MEM.MEMINFO.MemFree',
                              'MEM.MEMINFO.MemAvailable','MEM.MEMINFO.SwapTotal','MEM.MEMINFO.Dirty',
                              'MEM.BANDWIDTH.Total_Util','PERF.STAT.IPC',
                              'PERF.STAT.CACHE-MISS-RATIO', 'PERF.STAT.MPKI',
                              'PERF.STAT.ITLB-LOAD-MISS-RATIO', 'PERF.STAT.DTLB-LOAD-MISS-RATIO',
                              'PERF.STAT.SBPI', 'PERF.STAT.SBPC', 'MEM.VMSTAT.procs.b','MEM.VMSTAT.memory.swpd',
                              'MEM.VMSTAT.io.bo', 'MEM.VMSTAT.system.in', 'MEM.VMSTAT.system.cs',
                              'MEM.VMSTAT.util.swap', 'MEM.VMSTAT.util.cpu', 'MEM.VMSTAT.procs.r',
                              'SYS.TASKS.procs', 'SYS.TASKS.cswchs', 'SYS.LDAVG.runq-sz',
                              'SYS.LDAVG.plist-sz', 'SYS.LDAVG.ldavg-1', 'SYS.LDAVG.ldavg-5',
                              'SYS.FDUTIL.fd-util']

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
        
            # 计算和显示混淆矩阵
        cm = confusion_matrix(y_test, y_pred)
        print("Confusion Matrix:")
        print(cm)

        # 打印分类报告
        report = classification_report(y_test, y_pred)
        print("Classification Report:")
        print(report)
        
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
            tuned_parameters = [
                {'n_estimators': range(100, 400, 50), 'criterion': ['gini', 'entropy'],
                  'max_features': ['sqrt', 'log2']},
            ]
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
        
        x_train, x_test, y_train, y_test = tts(x_axis, y_axis, test_size=0.3, random_state=42)
        
        # Compute class weights
        class_weights = class_weight.compute_class_weight(class_weight='balanced', classes=np.unique(y_train), y=y_train)
        w_array = class_weights[y_train]

        model = XGBClassifier(
            learning_rate=0.1,
            n_estimators=400,
            max_depth=6,
            min_child_weight=0.5,
            gamma=0.01,
            subsample=1,
            colsample_bytree=1,
            random_state=27,
            use_label_encoder=False,  # 关闭标签编码器警告
            eval_metric='merror',  # 设置评估指标为 merror
        )
        
        model.fit(x_train, y_train, sample_weight=w_array)
        y_pred = model.predict(x_test)
        
        accuracy = accuracy_score(y_test, y_pred)
        print(f"The accuracy of XGBoost classifier is {accuracy}")

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

        self.parsing(data_path)

        x_type = self.dataset.iloc[:, :-1].copy()  # 提取特征数据 x_type，排除最后两列（类型和应用名）。
        self.scaler.fit_transform(x_type)
        y_app = self.aencoder.fit_transform(self.dataset.iloc[:, -1])
        joblib.dump(self.tencoder, tencoder_path)
        joblib.dump(self.aencoder, aencoder_path)
        joblib.dump(self.scaler, scaler_path)

        if feature_selection:
            x_type = self.feature_selection(x_type, y_app)

        self.rf_clf(x_type, y_app, search=search)
        print("The overall classifier has been generated.")

        for workload, group in self.dataset.groupby('workload.type'):
            x_app = self.scaler.transform(group.iloc[:, :-1].copy())
            y_app = self.aencoder.transform(group.iloc[:, -1])

            clf_name = workload + "_clf.m"
            feature_name = workload + "_feature.m"
            clf_path = os.path.join(self.model_path, clf_name)
            feature_path = os.path.join(self.model_path, feature_name)

            if feature_selection:
                x_app = self.feature_selection(x_app, y_app, feature_path)

            self.rf_clf(x_app, y_app, clfpath=clf_path, search=search)
            print(f"The {workload} classifier has been generated.")

    def identify(self, data, feature_selection=False):
        """
        identify the workload_type according to input data
        :param data:  input data
        """
        data = data[self.data_features]
        tencoder_path = os.path.join(self.model_path, "tencoder.pkl")
        aencoder_path = os.path.join(self.model_path, "aencoder.pkl")
        scaler_path = os.path.join(self.model_path, "scaler.pkl")

        self.scaler = joblib.load(scaler_path)
        self.tencoder = joblib.load(tencoder_path)
        self.aencoder = joblib.load(aencoder_path)

        data = self.scaler.transform(data)

        if feature_selection:
            feature_path = os.path.join(self.model_path, "total_feature.m")

            type_feat = joblib.load(feature_path)
            
            data = type_feat.transform(data)
        workload = self.rf_clf.predict(data)
        workload = self.tencoder.inverse_transform(workload)
        print("Current workload:", workload)
        
        prediction = collections.Counter(workload).most_common(1)[0]
        confidence = prediction[1] / len(workload)

        if confidence > 0.5:
            return prediction[0], confidence

        return "default", confidence

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
        x_type = self.dataset.iloc[:, :-1].copy()
        y_app = self.aencoder.fit_transform(self.dataset['workload.type'])
        joblib.dump(self.scaler, os.path.join(dirname, scalername))
        joblib.dump(self.aencoder, os.path.join(dirname, encodername))

        class_num = len(self.aencoder.classes_)
        if class_num == 1:
             y_app[-1] = (y_app[-1] + 1) % class_num
        self.svm_clf(x_type, y_app, custom_path)

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
