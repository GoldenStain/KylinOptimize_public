import csv

def find_potential_bottleneck_processes(process_data):
    """
    寻找可能存在性能瓶颈的进程ID列表

    :param process_data: 包含进程数据的字典数组，每个字典包括以下键：
                         'pid', 'name', 'sent_bytes', 'recv_bytes', 'sent_count', 'recv_count',
                         'disk_read_bytes', 'disk_write_bytes', 'disk_read_count', 'disk_write_count',
                         'cpu_usage', 'disk_read_wait', 'disk_write_wait', 'mem_usage', 'task_nvcsw', 'task_nivcsw'
    :return: 可能存在性能瓶颈的进程ID列表
    """
    thresholds = {
        'cpu_usage': 85,        
        'disk_read_wait': 100,
        'mem_usage': 9000000 
    }

    if not process_data:
        return []

    bottleneck_pids = []

    for process in process_data:
        try:
            is_bottleneck = False

            # Check each metric against its threshold
            for metric, threshold in thresholds.items():
                if metric in process and float(process[metric]) > threshold:
                    is_bottleneck = True
                    break  # No need to check further once a bottleneck condition is found

            if is_bottleneck:
                bottleneck_pids.append(process['pid'])
        except ValueError as e:
            print(f"Ignoring process due to invalid data: {process}, error: {str(e)}")
        except KeyError as e:
            print(f"Ignoring process due to missing key: {process}, error: {str(e)}")

    return bottleneck_pids

def load_process_data_from_csv(file_path):
    """
    从CSV文件加载进程数据

    :param file_path: CSV文件路径
    :return: 包含进程数据的字典数组
    """
    process_data = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                process_data.append(row)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"Error while loading CSV file '{file_path}': {str(e)}")
    return process_data

if __name__ == "__main__":
    csv_file_path = "/home/wsw/桌面/KylinDBOptimize/analysis/tests/testdata_proc_filter.csv"
    process_data = load_process_data_from_csv(csv_file_path)
    
    if process_data:
        print(f"Loaded {len(process_data)} processes from file '{csv_file_path}'")
        bottleneck_pids = find_potential_bottleneck_processes(process_data)
        
        if bottleneck_pids:
            print("可能存在性能瓶颈的进程ID列表:")
            print(bottleneck_pids)
        else:
            print("没有进程有明显的瓶颈")
    else:
        print(f"未能从文件 '{csv_file_path}' 加载进程数据.")
