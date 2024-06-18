from flask import Flask, render_template, redirect
import json
from . import globals

app = Flask(__name__)

dict_name = ["sent_bytes", "recv_bytes", "disk_read_bytes", "disk_write_bytes", "disk_read_count", "disk_write_count", "cpu_usage"]

@app.route('/')
def index():
    return redirect('/static/index.html', code=302, Response=None)

@app.route('/api/perf')
def api_perf():
    return json.dumps(globals.SYSTEM_INFO)

@app.route('/api/proc')
def api_proc():
    return json.dumps(globals.PROCESS_INFO)

def start(port):
    app.run(port=port)

if __name__ == '__main__':
    start()
