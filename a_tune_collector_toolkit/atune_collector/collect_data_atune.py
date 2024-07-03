#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2020 Huawei Technologies Co., Ltd.
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2020-11-13

"""
The main function for collecting data.
"""
import argparse
import json
import os
import time
import csv
import subprocess

from plugin.plugin import MPI
from werkzeug.utils import secure_filename


class Collector:
    """class for Collector"""

    def __init__(self, data):
        self.data = data
        self.field_name = []
        self.support_multi_block = ['storage']
        self.support_multi_nic = ['network', 'network-err']
        self.support_multi_app = ['process']
        self.monitors = self.parse_json()
        self.mpi = MPI()

    def parse_json(self):
        """parse json data"""
        monitors = []
        for item in self.data["collection_items"]:
            if item["name"] in self.support_multi_app and ('application' not in self.data or
                                                                self.data["application"] == ""):
                continue
            if item["name"] in self.support_multi_app:
                applications = self.data["application"].split(',')
                parameters = ["--interval=%s --app=%s;" %(self.data["interval"], self.data["application"])]
                for application in applications:    
                    for metric in item["metrics"]:
                        self.field_name.append(
                            "%s.%s.%s#%s" % (item["module"], item["purpose"], metric, application))
                        parameters.append("--fields=%s" % metric)
            else:
                parameters = ["--interval=%s;" % self.data["interval"]]
                for metric in item["metrics"]:
                    nics = self.data["network"].split(',')
                    blocks = self.data["block"].split(',')
                    
                    if item["name"] in self.support_multi_nic and len(nics) > 1:
                        for net in nics:
                            self.field_name.append(
                                "%s.%s.%s#%s" % (item["module"], item["purpose"], metric, net))
                    elif item["name"] in self.support_multi_block and len(blocks) > 1:
                        for block in blocks:
                            self.field_name.append(
                                "%s.%s.%s#%s" % (item["module"], item["purpose"], metric, block))
                    else:
                        self.field_name.append("%s.%s.%s" % (item["module"], item["purpose"], metric))
                    parameters.append("--fields=%s" % metric)
                if "threshold" in item:
                    parameters.append("--threshold=%s" % item["threshold"])

            parameters.append("--nic=%s" % self.data["network"])
            parameters.append("--device=%s" % self.data["block"])
            monitors.append([item["module"], item["purpose"], " ".join(parameters)])
        return monitors

    def collect_data(self):
        """collect data"""
        raw_data = self.mpi.get_monitors_data(self.monitors)
        float_data = [float(num) for num in raw_data]
        return float_data


def start_collect_atune(arg_json_path):
    current_user = os.getlogin()
    json_path = "./a_tune_collector_toolkit/atune_collector/collect_data.json"
    if arg_json_path:
        json_path = arg_json_path
    with open(json_path, 'r') as file:
        json_data = json.load(file)
    filename = secure_filename(json_path)
    collector = Collector(json_data)
    path = os.path.abspath(os.path.expanduser(os.path.expandvars(collector.data["output_dir"])))
    if not os.path.exists(path):
        os.makedirs(path, 0o750)
    try:
        collect_num = collector.data["sample_num"]
        if int(collect_num) < 1:
            os.abort("sample_num must be greater than 0")
        file_name = "{}-{}.csv".format(collector.data.get("workload_type", "default"), int(round(time.time() * 1000)))

        print("csv path: %s" % os.path.join(path, file_name))
        print("csv fields: %s" % " ".join(collector.field_name))
        print("start to collect data...")
        with open(os.path.join(path, file_name), "w") as csvfile:
            writer = csv.writer(csvfile)
            output_fields = ["TimeStamp"] + collector.field_name
            writer.writerow(output_fields)
            csvfile.flush()
            for _ in range(collect_num):
                data = collector.collect_data()
                str_data = [str(round(value, 3)) for value in data]
                str_data.insert(0, time.strftime("%H:%M:%S"))
                writer.writerow(str_data)
                csvfile.flush()
                print(" ".join(str_data))
        print("finish to collect data, csv path is %s" % os.path.join(path, file_name))

    except KeyboardInterrupt:
        print("user stop collect data")

    subprocess.run(['chown', current_user, f'{path}/{file_name}'], capture_output=False)