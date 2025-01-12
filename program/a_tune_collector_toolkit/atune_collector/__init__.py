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
Init file.
"""

import sys
import os
import json
from . import shared
from .collect_data_atune import Collector
sys.path.insert(0, os.path.dirname(__file__))

json_path = "./program/a_tune_collector_toolkit/atune_collector/collect_data.json"
with open(json_path, 'r') as file:
    json_data = json.load(file)
shared.GET_COLLECTOR = Collector(json_data)

