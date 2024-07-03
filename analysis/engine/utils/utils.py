"""
Provide an interface to read data from csv.
"""

import re
import datetime
import shutil
import logging
import tarfile
import pandas as pd
import numpy as np
from pathlib import Path

from analysis.engine.config import EngineConfig


def read_from_csv(path):
    """read data from csv"""
    if not Path(path).exists():
        return None
    if not path.endswith('.csv'):
        return None

    with open(path, 'r', encoding='utf-8') as file:
        data = pd.read_csv(file, header=0)

    return data


def extract_file(file_path, target_path):
    """extract file"""
    tar = tarfile.open(file_path)
    logging.debug("%s", tar.getnames())
    tar.extractall(path=target_path)
    tar.close()
    res_path = file_path.rpartition('-')[0]
    return res_path




def get_time_difference(end_time, start_time):
    """get time difference in second"""
    end_time += "000"
    start_time += "000"
    end = [int(ele) for ele in re.split(r"-| |:|\.", end_time)]
    start = [int(ele) for ele in re.split(r"-| |:|\.", start_time)]
    date_end = datetime.datetime(end[0], end[1], end[2], end[3], end[4], end[5], end[6])
    date_start = datetime.datetime(start[0], start[1], start[2],
                                   start[3], start[4], start[5], start[6])
    return str((date_end - date_start).total_seconds())


def get_opposite_num(num, opposite):
    """get opposite number for string"""
    if num[0] == "-":
        return num[1:]
    if opposite and num[0] != "-":
        return "-" + num
    return num


def get_string_split(line, index, key, val):
    """get split value for line"""
    params = ""
    for element in line.split("|")[index].split(","):
        params += val + element.split("=")[key] + ","
    return params


def zip_key_value(key, val_array):
    """zip key and value together"""
    res = []
    for line in val_array:
        res.append(dict(zip(key, line)))
    return res


def get_tuning_options(param):
    """get options by current env value, range, and step"""
    if param is None or param["range"] is None or param["step"] == 0 or \
            param["options"] is not None:
        return param

    values = re.findall(r'[0-9]+', param["ref"])
    multiples = []
    for i in np.arange(param["range"][0], param["range"][1], param["step"]):
        multiples.append(i)
    if multiples[len(multiples) - 1] + param["step"] == param["range"][1]:
        multiples.append(param["range"][1])
    logging.info("the multiples are: %s", ' '.join(str(x) for x in multiples))
    options = []
    for mul in multiples:
        options.append(get_multiple_res(values, mul))
    param["options"] = options
    param["step"] = 0
    param["range"] = None
    return param


def get_multiple_res(values, mul):
    """get string multiple result"""
    res = ""
    mul = str(mul)
    floats = 0
    spl = mul.split('.')
    if len(spl) == 2:
        floats = len(spl[1])
        mul = spl[0] + spl[1]
    for value in values:
        spl_val = value.split('.')
        if len(spl_val) == 2:
            floats += len(spl_val[1])
            value = spl_val[0] + spl_val[1]
        val_len = len(value)
        mul_len = len(mul)
        res_arr = [0] * (val_len + mul_len)
        for i in range(val_len - 1, -1, -1):
            x = int(value[i])
            for j in range(mul_len - 1, -1, -1):
                res_arr[i + j + 1] += x * int(mul[j])

        for i in range(val_len + mul_len - 1, 0, -1):
            res_arr[i - 1] += res_arr[i] // 10
            res_arr[i] %= 10

        index = 1 if res_arr[0] == 0 else 0
        if floats != 0:
            res += "".join(str(x) for x in res_arr[index:]).lstrip('0')[:-floats] + " "
        else:
            res += "".join(str(x) for x in res_arr[index:]).lstrip('0') + " "
    logging.info("The options would be: %s", res[:-1])
    return res[:-1]


def is_analysis_data(data):
    """Determine whether the data is a fixed type of analysis"""
    data_types = []
    for key in data:
        data_types.append(key)
    return data_types.sort() == EngineConfig.db_analysis_type.sort()