from . import globals
import time

def log_debug(msg):
    if globals.LOG_LEVEL > globals.LOG_LEVEL_DEBUG:
        return
    time_s = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    globals.LOG_FILE.write(f'{time_s} [DEBUG] {msg}\n')
    globals.LOG_FILE.flush()

def log_info(msg):
    if globals.LOG_LEVEL > globals.LOG_LEVEL_INFO:
        return
    time_s = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    globals.LOG_FILE.write(f'{time_s} [INFO] {msg}\n')
    globals.LOG_FILE.flush()

def log_warning(msg):
    if globals.LOG_LEVEL > globals.LOG_LEVEL_WARNING:
        return
    time_s = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    globals.LOG_FILE.write(f'{time_s} [WARNING] {msg}\n')
    globals.LOG_FILE.flush()

def log_error(msg):
    if globals.LOG_LEVEL > globals.LOG_LEVEL_ERROR:
        return
    time_s = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    globals.LOG_FILE.write(f'{time_s} [ERROR] {msg}\n')
    globals.LOG_FILE.flush()