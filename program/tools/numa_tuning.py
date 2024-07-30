from flask import Flask, jsonify, request
import subprocess
import os

app = Flask(__name__)

class NumadManager:
    @staticmethod
    def detect_cross_numa_access():
        numa_maps_path = "/proc/self/numa_maps"
        cross_numa_access = False
        try:
            with open(numa_maps_path, 'r') as file:
                for line in file:
                    if 'N0' in line and 'N1' in line:  # Assuming two NUMA nodes N0 and N1
                        cross_numa_access = True
                        break
        except FileNotFoundError:
            pass
        return cross_numa_access

    @staticmethod
    def run_numad():
        try:
            result = subprocess.run(['numad'], capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"An error occurred: {e}"
        
    @staticmethod
    def close_numad():
        try:
            result = subprocess.run(['numad', '-i', '0'], capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"An error occurred: {e}"

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the NUMA Tuning API"})

@app.route('/status')
def status():
    cross_numa = NumadManager.detect_cross_numa_access()
    numad_output = ""
    if cross_numa:
        numad_output = NumadManager.run_numad()
    return jsonify({
        "cross_numa": cross_numa,
        "numad_output": numad_output
    })

@app.route('/toggle-numa', methods=['POST'])
def toggle_numa():
    enable_numa = request.json.get("enable")
    if enable_numa:
        # Here you can add logic to enable NUMA if needed
        return jsonify({"success": True, "message": "NUMA enabled"}), 200
    else:
        try:
            result = NumadManager.close_numad()
            return jsonify({"success": True, "message": "NUMA disabled", "output": result}), 200
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/optimize', methods=['POST'])
def optimize():
    cross_numa = NumadManager.detect_cross_numa_access()
    if cross_numa:
        try:
            result = NumadManager.run_numad()
            return jsonify({"success": True, "message": "Optimization performed", "output": result}), 200
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    else:
        return jsonify({"success": True, "message": "No optimization needed", "output": ""}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
