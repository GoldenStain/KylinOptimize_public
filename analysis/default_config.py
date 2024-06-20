import ast
import logging

"""
Default path config.
"""
LOCAL_ADDRS = '/var/run/Ktuned/Ktuned.sock'
REST_CERT_PATH = '/etc/Ktuned/rest_certs/'
ENGINE_CERT_PATH = '/etc/Ktuned/engine_certs/'
UI_CERT_PATH = '/etc/Ktuned/ui_certs/'
GRPC_CERT_PATH = '/etc/Ktuned/grpc_certs'
ANALYSIS_DATA_PATH = '/var/Ktune_data/analysis/'
TUNING_DATA_PATH = '/var/Ktune_data/tuning/'
TUNING_DATA_DIRS = ['running', 'finished', 'error']
TRAINING_MODEL_PATH = '/usr/libexec/Ktuned/analysis/models/'


def get_or_default(config, section, key, value):
    """get or default param"""
    if config.has_option(section, key):
        return config.get(section, key)
    return value


def get_or_default_bool(config, section, key, value):
    """get or default boolean param"""
    if config.has_option(section, key):
        return config.get(section, key).lower() == 'true'
    return value


def get_or_default_list(config, section, key, value):
    """get or default list param"""
    if config.has_option(section, key):
        try:
            return ast.literal_eval(config.get(section, key))
        except (SyntaxError, ValueError) as e:
            logging.error(f"Error parsing list from config: {section}.{key}. Error: {e}")
    return value
