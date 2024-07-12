#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2019 Huawei Technologies Co., Ltd.
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2019-10-29

"""
The sub class of the monitor, used to collect memory bandwidth stat info.
"""
import inspect
import logging
import subprocess
import getopt
import re
import json

from ..common import Monitor
from ..memory import topo

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s: %(message)s')
LOGGER = logging.getLogger(__name__)


class MemBandwidth(Monitor):
    """To collect memory bandwidth stat info"""
    _module = "MEM"
    _purpose = "BANDWIDTH"
    _option = "-a -e cache-misses,cache-references,cycles,instructions --interval-print {int} --interval-count 1"

    def __init__(self, user=None):
        Monitor.__init__(self, user)
        self.__cmd = "perf stat"
        self.__interval = 1000

        self.__cnt = {
            "Total": 0,
            "CacheMisses": 0,
            "Bandwidth": 0.0,
            "Total_Max": 0,
            "Total_Util": 0.0
        }

        self.__cache_line_size = 64  # 假设缓存行大小为64字节
        self.__cnt["Total_Max"] = self.__get_theory_bandwidth()  # 计算理论最大带宽
        # print(f'{self.__cnt["Total_Max"]} GB/s')

        # LOGGER.info("Monitor initialized for cache-misses, cache-references, cycles, instructions")

    def _get(self, para=None):
        if para is not None:
            opts, _ = getopt.getopt(para.split(), None, ['interval='])
            for opt, val in opts:
                if opt in '--interval':
                    if val.isdigit():
                        self.__interval = int(val) * 1000
                    else:
                        err = ValueError(
                            "Invalid parameter: {opt}={val}".format(
                                opt=opt, val=val))
                        LOGGER.error("%s.%s: %s", self.__class__.__name__,
                                     inspect.stack()[0][3], str(err))
                        raise err
                    continue

        output = subprocess.check_output(
            "{cmd} {opt}".format(
                cmd=self.__cmd,
                opt=self._option.format(
                    int=self.__interval,)).split(),
            stderr=subprocess.STDOUT)
        return output.decode()
# 待完善
    @staticmethod
    def __get_theory_bandwidth():
        max_bandwidth = 76800 # 以MB/s为单位
        return max_bandwidth

    def __read_counters(self, perf_output):
        pattern = r"^\s*\S+\s+(\d[\d,]*)\s+cache-misses"
        match = re.search(pattern, perf_output, re.MULTILINE)
        if match:
            cache_misses = int(match.group(1).replace(",", ""))
            print(f'cache_misses : {cache_misses}')
            self.__cnt["CacheMisses"] = cache_misses
            self.__cnt["Bandwidth"] = (cache_misses * self.__cache_line_size) / (self.__interval / 1000.0) / 1024 / 1024
            self.__cnt["Total"] = self.__cnt["Bandwidth"]
            if self.__cnt["Total_Max"] != 0:
                self.__cnt["Total_Util"] = (self.__cnt["Total"] / self.__cnt["Total_Max"])
            # LOGGER.info("Cache Misses: %d, Estimated Bandwidth: %.2f MB/s, Utilization: %.2f%%",
            #             cache_misses, self.__cnt["Bandwidth"], self.__cnt["Total_Util"])

    def decode(self, info, para):
        """
        decode the result of the operation
        :param info:  content that needs to be decoded
        :param para:  command line argument
        :returns ret:  operation result
        """
        if para is None:
            return info

        self.__read_counters(info)
        fields = []
        ret = ""

        opts, _ = getopt.getopt(para.split(), None, ['nic=', 'fields=', 'device='])
        for opt, val in opts:
            if opt in '--fields':
                fields.append(val)
                continue

        for field in fields:
            ret = ret + " {:.2f}".format(self.__cnt.get(field, 0))
        return ret
