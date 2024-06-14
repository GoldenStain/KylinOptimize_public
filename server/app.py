from flask import Flask, render_template, redirect
import json
import globals

app = Flask(__name__)


@app.route('/')
def index():
    return redirect('/static/index.html', code=302, Response=None)

@app.route('/api/perf')
def api_perf():
    data = {
        "cpu": globals.CPU_USAGE,
        "memory": globals.MEMORY_USAGE,
        "block_io": globals.BLOCK_IO_USAGE,
        "block_io_cnt": globals.BLOCK_IO_CNT,
        "net_io": globals.NET_IO_USAGE,
        "net_io_cnt": globals.NET_IO_CNT
    }
    return json.dumps(data)

@app.route('/api/proc')
def api_proc():
    data = [{
        "name": "mysqld",
        "block_io": 164,
        "net_io": 23
    },
    {
        "name": "influxDB",
        "block_io": 86,
        "net_io": 68
    }]
    return json.dumps(data)

def start():
    app.run()

if __name__ == '__main__':
    start()
