
"""
Initial engine config parameters.
"""

class EngineConfig:
    """Initial engine config parameters"""

    engine_host = 'localhost'
    engine_port = '3838'
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
    cpu_usage = '50'
    task_nvcsw = '100'
    task_nivcsw = '10'
    mem_usage = '60'
    sent_bytes = '1000'
    recv_bytes = '800'
    sent_count = '50'
    recv_count = '30'
    disk_read_bytes = '500'
    disk_write_bytes = '300'
    disk_read_count = '200'
    disk_write_count = '150'
    disk_read_wait = '5'
    disk_write_wait = '3'

    @staticmethod
    def initial_params():
        """Initial all params"""
        return True
