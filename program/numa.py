import subprocess

def get_cpu_affinity(pid):
    try:
        result = subprocess.check_output(['taskset', '-p', str(pid)], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Error getting affinity for PID {pid}: {e}"

def set_cpu_affinity(pid, cpus):
    cpu_list = ','.join(map(str, cpus))
    try:
        result = subprocess.run(['taskset', '-pc', cpu_list, str(pid)], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error setting affinity for PID {pid}: {e}")
    except FileNotFoundError:
        print(f"Process ID: {pid} does not exist")
    except PermissionError:
        print(f"Permission denied: Failed to set affinity for PID {pid}")
    except Exception as e:
        print(f"Error setting affinity for PID {pid}: {e}")

