import ast
import logging


"""
Default path config.
"""
ANALYSIS_DATA_PATH = '/var/ktune_data/analysis/'
TUNING_DATA_PATH = '/var/ktune_data/tuning/'
TUNING_DATA_DIRS = ['running', 'finished', 'error']
TRAINING_MODEL_PATH = '/usr/libexec/ktuned/analysis/models/'


def get_or_default(config, section, key, value):
    """get or default param"""
    if config.has_option(section, key):
        return config.get(section, key)
    return value

