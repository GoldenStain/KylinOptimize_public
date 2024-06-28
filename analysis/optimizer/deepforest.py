import numpy as np
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
import logging

LOGGER = logging.getLogger(__name__)


class CascadeForestClassifier:

    def __init__(self, n_estimators=10, max_layers=10, random_state=None):
        self.n_estimators = n_estimators
        self.max_layers = max_layers
        self.random_state = random_state
        self.layers = []

    def fit(self, x, y):
        layer = 0
        while layer < self.max_layers:
            LOGGER.info('space %s', layer + 1)
            layer_estimators = []
            for i in range(self.n_estimators):
                if i % 2 == 0:
                    estimator = RandomForestClassifier(n_jobs=-1, random_state=self.random_state)
                else:
                    estimator = ExtraTreesClassifier(n_jobs=-1, random_state=self.random_state)
                estimator.fit(x, y)
                layer_estimators.append(estimator)
            self.layers.append(layer_estimators)
            x_new = self._generate_features(x)
            if np.array_equal(x, x_new):
                break
            x = x_new
            layer += 1

    def predict(self, x):
        x_new = x
        for layer_estimators in self.layers:
            x_new = self._generate_features(x_new, layer_estimators)
        return np.argmax(x_new, axis=1)

    def _generate_features(self, X, layer_estimators=None):
        if layer_estimators is None:
            layer_estimators = self.layers[-1]
        features = []
        for estimator in layer_estimators:
            probas = estimator.predict_proba(X)
            features.extend(np.transpose(probas))
        return np.column_stack(features)


