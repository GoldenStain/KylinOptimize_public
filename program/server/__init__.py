import json
import globals
import time

config = json.load(open("config.json"))

globals.TIME_INTERVAL = config["time_interval"]
globals.LOG_PATH = config["log_path"]
globals.LOG_LEVEL = config["log_level"]

globals.LOG_FILE = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ".log"
globals.LOG_FILE = open(globals.LOG_PATH + globals.LOG_FILE, "a")

log_level = globals.LOG_LEVEL_DEBUG # 默认
if globals.LOG_LEVEL == "info":
    log_level = globals.LOG_LEVEL_INFO
elif globals.LOG_LEVEL == "warning":
    log_level = globals.LOG_LEVEL_WARNING
elif globals.LOG_LEVEL == "error":
    log_level = globals.LOG_LEVEL_ERROR
globals.LOG_LEVEL = log_level