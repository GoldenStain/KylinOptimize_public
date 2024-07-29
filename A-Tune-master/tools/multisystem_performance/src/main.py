#!/usr/bin/bash

# Copyright (c) 2022 Huawei Technologies Co., Ltd.
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.

# #############################################
# @Author    :   westtide
# @Contact   :   tocokeo@outlook.com
# @Date      :   2023/9/22
# @License   :   Mulan PSL v2
# @Desc      :   main function of multisystem performance analysis
# #############################################

from global_var import _init
from run_benchmark import benchmark
from load_check import dependence_check
from modify_parameters import modify_parameters
from process_parameters import process_parameters


def main():

    _init()

    # 检查+-依赖
    dependence_check()

    # 获取、对比、存储参数参数
    process_parameters()

    # 修改 sysctl 参数 ulimit 参数
    modify_parameters()

    # 性能测试
    benchmark()


if __name__ == '__main__':
    main()
