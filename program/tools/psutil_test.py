import psutil
import time

attrs = ['pid', 'name', 'cpu_percent']
print('\t'.join(attrs))
for proc in psutil.process_iter(attrs):
    info = map(str, [proc.info[attr] for attr in attrs])
    print('\t'.join(info))
