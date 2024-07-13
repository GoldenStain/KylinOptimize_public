import argparse
import json
import os
import time
import traceback
import csv
import subprocess
import sys
import threading
import pandas as pd

TABLE_SIZE = '1000'

commands = [
    ['sysbench', 'cpu', '--cpu-max-prime=200000', '--threads=8', '--time=60', 'run'],
    [
        'sysbench',
        '--db-driver=mysql',
        '--mysql-db=sbtest',
        '--mysql-user=root',
        '--mysql-password=mysql123456',
        '--table-size=' + TABLE_SIZE,
        '--tables=10',
        '/usr/share/sysbench/oltp_read_write.lua',
        'prepare'
    ],
    [
        'sysbench',
        '--db-driver=mysql',
        '--mysql-db=sbtest',
        '--mysql-user=root',
        '--mysql-password=mysql123456',
        '--table-size=' + TABLE_SIZE,
        '--tables=10',
        '--threads=14',
        '--time=120',
        '/usr/share/sysbench/oltp_read_write.lua',
        'run'
    ],
    [
        'sysbench',
        '--db-driver=mysql',
        '--mysql-db=sbtest',
        '--mysql-user=root',
        '--mysql-password=mysql123456',
        '--tables=10',
        '/usr/share/sysbench/oltp_read_write.lua',
        'cleanup'
    ],
    [
		'/home/xjbo/桌面/inch/inch',
    	'-b', '1000',
    	'-c', '14',
    	'-db', 'Stress',
    	'-host', 'http://localhost:8086',
    	'-p', '1000',
    	'-m', '5',
    	'-t', '100,10',
        '-f', '3',
    	'-token', 'bvYd9DG4n5IlVLUKLIeay7zJkxrhJRFVXmCIbuJPaff_5cHknvUPKmaK6urdRQLRDRVHsXFh2Umuwro6lb4I6g==',
    	'-vhosts', '8',
    	'-v', '--v2',
        '-time', '600s',
        '-shard-duration', '1h'
	],# 4
    ['stress-ng', '--vm', '2', '--vm-bytes', '8G', '--vm-method', 'all', '--verify', '-t', '90s'],
    ['sysbench', 'fileio', '--file-total-size=10G', 'prepare'],
    ['sysbench', 'fileio', '--file-total-size=10G', '--file-test-mode=rndrw', '--time=120', '--max-requests=0', 'run'],
    ['sysbench', 'fileio', '--file-total-size=10G', 'cleanup'],#8
    ['iperf3', '-c', '127.0.0.1', '-b', '10000M', '-t', '60']
]

if __name__ == "__main__":
	subprocess.Popen(commands[9])
	subprocess.Popen(commands[0])