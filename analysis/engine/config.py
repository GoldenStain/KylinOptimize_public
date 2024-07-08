"""
Initial engine config parameters.
"""

import os
from configparser import ConfigParser
from analysis.default_config import get_or_default


class EngineConfig:
    """initial engine config parameters"""

    engine_host = ''
    engine_port = ''
    engine_tls = False
    engine_ca_file = ''
    engine_server_cert = ''
    engine_server_key = ''
    level = ''
    log_dir = None
    db_enable = False
    database = ''
    db_host = ''
    db_port = ''
    db_name = ''
    db_user_name = ''
    db_user_passwd = ''
    db_passwd_key = ''
    db_passwd_iv = ''
    db_analysis_type = []

    @staticmethod
    def initial_params(filename):
        """initial all params"""
        if not os.path.exists(filename):
            return False
        config = ConfigParser()
        config.read(filename)
        EngineConfig.engine_host = get_or_default(config, 'server', 'engine_host', 'localhost')
        EngineConfig.engine_port = get_or_default(config, 'server', 'engine_port', '3838')
        EngineConfig.level = get_or_default(config, 'log', 'level', 'info')
        EngineConfig.log_dir = get_or_default(config, 'log', 'level', None)
        
        # bottleneck
        # computing
        EngineConfig.cpu_stat_util = get_or_default(config, 'bottleneck', 'cpu_stat_util', '80')
        EngineConfig.cpu_stat_cutil = get_or_default(config, 'bottleneck', 'cpu_stat_cutil', '80')
        EngineConfig.perf_stat_ipc = get_or_default(config, 'bottleneck', 'perf_stat_ipc', '1')
        # memory
        EngineConfig.mem_bandwidth_total_util = get_or_default(config, 'bottleneck', 'mem_bandwidth_total_util', '70')
        EngineConfig.mem_vmstat_util_swap = get_or_default(config, 'bottleneck', 'mem_vmstat_util_swap', '70')
        EngineConfig.mem_vmstat_util_cpu = get_or_default(config, 'bottleneck', 'mem_vmstat_util_cpu', '70')
        # network
        EngineConfig.net_stat_ifutil = get_or_default(config, 'bottleneck', 'net_stat_ifutil', '70')
        EngineConfig.net_estat_errs = get_or_default(config, 'bottleneck', 'net_estat_errs', '1')
        # network I/O
        EngineConfig.net_stat_rxkbs = get_or_default(config, 'bottleneck', 'net_stat_rxkbs', '70')
        EngineConfig.net_stat_txkbs = get_or_default(config, 'bottleneck', 'net_stat_txkbs', '70')
        #disk I/OF
        EngineConfig.storage_stat_util = get_or_default(config, 'bottleneck', 'storage_stat_util', '70')
            
        return True