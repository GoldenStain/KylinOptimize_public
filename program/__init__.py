import os
import time
from subprocess import run, PIPE
from subprocess import run, CalledProcessError

class TuningManager:
    def __init__(self, project_name, config_file, log_file="tuning_result.log"):
        self.project_name = project_name
        self.config_file = config_file
        self.log_file = log_file

    def set_tuning(self):
        """
        启动调优过程，并等待调优结束。
        """
        command = f"sudo atune-adm tuning --project {self.project_name} --detail {self.config_file}"
        try:
            with open(self.log_file, "w") as log:
                result = run(command, shell=True, stdout=log, stderr=log, text=True, check=True)

            print("调优过程启动成功")
            time.sleep(20)  # 等待20秒或适当的时间
        except CalledProcessError as e:
            print(f"调优过程启动失败: {e.stderr}")
        except PermissionError:
            print("需要管理员权限来运行此命令。请确保您有足够的权限。")

    def get_tuning_result(self):
        """
        获取调优结果。
        """
        if os.path.exists(self.log_file):
            with open(self.log_file, "r") as log:
                return log.read()
        else:
            print("日志文件不存在")
            return None

    def restore_environment(self):
        """
        恢复环境。
        """
        command = f"sudo atune-adm tuning --restore --project {self.project_name}"
        try:
            result = run(command, shell=True, capture_output=True, text=True, check=True)
            print("环境恢复成功")
        except CalledProcessError as e:
            print(f"环境恢复失败: {e.stderr}")
        except PermissionError:
            print("需要管理员权限来运行此命令。请确保您有足够的权限。")