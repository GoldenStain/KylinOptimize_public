from analysis.engine.config import EngineConfig
import logging

LOGGER = logging.getLogger(__name__)


class BottleneckCharacterization:

    def __init__(self):
        self.cpu_thresholds = {
            'cpu_usage': float(EngineConfig.cpu_usage),
        }

        self.disk_io_thresholds = {
            'disk_read_bytes': float(EngineConfig.disk_read_bytes),
            'disk_write_bytes': float(EngineConfig.disk_write_bytes),
            'disk_read_count': float(EngineConfig.disk_read_count),
            'disk_write_count': float(EngineConfig.disk_write_count),
            'disk_read_wait': float(EngineConfig.disk_read_wait),
            'disk_write_wait': float(EngineConfig.disk_write_wait),
        }

        self.mem_thresholds = {
            'mem_usage': float(EngineConfig.mem_usage),
        }

        self.network_thresholds = {
            'sent_bytes': float(EngineConfig.sent_bytes),
            'recv_bytes': float(EngineConfig.recv_bytes),
            'sent_count': float(EngineConfig.sent_count),
            'recv_count': float(EngineConfig.recv_count),
        }

        self.task_thresholds = {
            'task_nvcsw': float(EngineConfig.task_nvcsw),
            'task_nivcsw': float(EngineConfig.task_nivcsw),
        }

    def search_bottleneck(self, data):
        cpu_exist = self.check_thresholds(data, self.cpu_thresholds, "computational")
        mem_exist = self.check_thresholds(data, self.mem_thresholds, "memory")
        disk_io_exist = self.check_thresholds(data, self.disk_io_thresholds, "disk I/O")
        network_exist = self.check_thresholds(data, self.network_thresholds, "network")
        task_exist = self.check_thresholds(data, self.task_thresholds, "context switching")

        return cpu_exist, mem_exist, disk_io_exist, network_exist, task_exist

    def check_thresholds(self, data, thresholds, bottleneck_type):
        bottleneck_found = False
        for key, threshold in thresholds.items():
            if data.get(key) is not None and data[key].mean() >= threshold:
                LOGGER.info('There is a %s bottleneck in %s', bottleneck_type, key)
                bottleneck_found = True
        return bottleneck_found

