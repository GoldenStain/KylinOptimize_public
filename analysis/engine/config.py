"""
Initial engine config parameters.
"""

import os
from configparser import ConfigParser
from analysis.default_config import ENGINE_CERT_PATH
from analysis.default_config import get_or_default, get_or_default_bool, get_or_default_list


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
    #  数据库密码的加密向量。
    db_passwd_iv = ''
    #  数据库分析类型的列表。
    db_analysis_type = []

    @staticmethod
    def initial_params(filename):
        """initial all params"""
        if not os.path.exists(filename):
            return False
        config = ConfigParser()
        config.read(filename)

        # 读取 server 部分的配置
        EngineConfig.engine_host = get_or_default(config, 'server', 'engine_host', 'localhost')
        EngineConfig.engine_port = get_or_default(config, 'server', 'engine_port', '3838')
        EngineConfig.engine_tls = get_or_default_bool(config, 'server', 'engine_tls', False)

        # 如果启用 TLS，读取相关配置
        if EngineConfig.engine_tls:
            EngineConfig.engine_ca_file = get_or_default(config, 'server',
                                                         'tlsenginecacertfile', ENGINE_CERT_PATH + 'ca.crt')
            EngineConfig.engine_server_cert = get_or_default(config, 'server',
                                                             'tlsengineservercertfile', ENGINE_CERT_PATH + 'server.crt')
            EngineConfig.engine_server_key = get_or_default(config, 'server',
                                                            'tlsengineserverkeyfile', ENGINE_CERT_PATH + 'server.key')

        # 读取 log 部分的配置
        EngineConfig.level = get_or_default(config, 'log', 'level', 'info')
        EngineConfig.log_dir = get_or_default(config, 'log', 'level', None)

        # 读取 database 部分的配置
        EngineConfig.db_enable = get_or_default_bool(config, 'database', 'db_enable', False)
        if EngineConfig.db_enable:
            EngineConfig.database = get_or_default(config, 'database', 'database', 'MySQL')
            EngineConfig.db_host = get_or_default(config, 'database', 'db_host', 'localhost')
            EngineConfig.db_port = get_or_default(config, 'database', 'db_port', '3306')
            EngineConfig.db_name = get_or_default(config, 'database', 'db_name', 'Ktune_db')
            EngineConfig.db_user_name = get_or_default(config, 'database', 'db_user_name', 'admin')
            EngineConfig.db_user_passwd = get_or_default(config, 'database', 'db_user_passwd', '')
            EngineConfig.db_passwd_key = get_or_default(config, 'database', 'db_passwd_key', '')
            EngineConfig.db_passwd_iv = get_or_default(config, 'database', 'db_passwd_iv', '')
            EngineConfig.db_analysis_type = get_or_default_list(config, 'database', 'db_analysis_type', [])

        # bottleneck
        # computing
        EngineConfig.cpu_usage = get_or_default(config, 'bottleneck', 'cpu_usage', '50')
        EngineConfig.task_nvcsw = get_or_default(config, 'bottleneck', 'task_nvcsw', '100')
        EngineConfig.task_nivcsw = get_or_default(config, 'bottleneck', 'task_nivcsw', '10')
        # memory
        EngineConfig.mem_usage = get_or_default(config, 'bottleneck', 'mem_usage', '60')        # network
        # network
        EngineConfig.sent_bytes = get_or_default(config, 'bottleneck', 'sent_bytes', '1000')
        EngineConfig.recv_bytes = get_or_default(config, 'bottleneck', 'recv_bytes', '800')
        EngineConfig.sent_count = get_or_default(config, 'bottleneck', 'sent_count', '50')
        EngineConfig.recv_count = get_or_default(config, 'bottleneck', 'recv_count', '30')
        # disk I/O
        EngineConfig.disk_read_bytes = get_or_default(config, 'bottleneck', 'disk_read_bytes', '500')
        EngineConfig.disk_write_bytes = get_or_default(config, 'bottleneck', 'disk_write_bytes', '300')
        EngineConfig.disk_read_count = get_or_default(config, 'bottleneck', 'disk_read_count', '200')
        EngineConfig.disk_write_count = get_or_default(config, 'bottleneck', 'disk_write_count', '150')
        EngineConfig.disk_read_wait = get_or_default(config, 'bottleneck', 'disk_read_wait', '5')
        EngineConfig.disk_write_wait = get_or_default(config, 'bottleneck', 'disk_write_wait', '3')

        return True
