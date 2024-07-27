from flask import *
import json
from . import globals
from .. import optimize
from program.ebpf import flame_graph
from program.a_tune_collector_toolkit.atune_collector.collect_data_atune import get_data_return_confidence

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

@app.route('/api/flame_graph')
def api_flame_graph():
    if request.args.__contains__("cmd"):
        flame_graph.gen_flame_graph_mysql("program/server/static/flame_graph", request.args["cmd"], 50)
    else:
        flame_graph.gen_flame_graph_perf("program/server/static/flame_graph", 50)
    return redirect('/static/flame_graph.svg', code=302, Response=None)

@app.route('/api/confidence')
def api_confidence():
    return json.dumps(get_data_return_confidence())

@app.route('/api/optimize', methods=['POST'])
def api_optimize():
    data = request.get_json()
    if data.__contains__("flag"):
        optimize.set_policy_flags(data["flag"])
    return json.dumps(optimize.get_policy_flags())

def start(port):
    app.run(port=port)

if __name__ == '__main__':
    start()
