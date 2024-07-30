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
    if not globals.ENABLE_PERFORMANCE_DISPLAY:
        return {}, 403
    return json.dumps(globals.SYSTEM_INFO)

@app.route('/api/proc')
def api_proc():
    if not globals.ENABLE_PERFORMANCE_DISPLAY:
        return json.dumps([])
    return json.dumps(globals.PROCESS_INFO)

@app.route('/api/flame_graph')
def api_flame_graph():
    if request.args.__contains__("cmd") and request.args.__contains__("name"):
        flame_graph.gen_flame_graph_cmd("program/server/static/flame_graph", request.args["name"], request.args["cmd"], 50)
    else:
        flame_graph.gen_flame_graph_perf("program/server/static/flame_graph", 50)
    return redirect('/static/flame_graph.svg', code=302, Response=None)

@app.route('/api/confidence')
def api_confidence():
    return json.dumps(get_data_return_confidence())

@app.route('/api/optimize')
def api_optimize():
    if request.args.__contains__("flag"):
        o = json.loads(request.args["flag"])
        optimize.set_policy_flags(o)
    return json.dumps(optimize.get_policy_flags())

def start(port):
    app.run(port=port)

if __name__ == '__main__':
    start()
