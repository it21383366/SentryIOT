from flask import Flask, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# Paths to log file and flag file
LOG_FILE = os.path.join(os.path.dirname(__file__), "detection_log.jsonl")

@app.route("/latest", methods=["GET"])
def latest_result():
    try:
        if not os.path.exists(LOG_FILE):
            return jsonify({"message": "No detection yet"}), 200

        with open(LOG_FILE, "r") as f:
            lines = f.readlines()
            lines = [line.strip() for line in lines if line.strip()]
            lines = [json.loads(line) for line in lines if line.startswith("{") and line.endswith("}")]
            if not lines:
                return jsonify({"message": "No detection yet"}), 200

            latest = lines[-1]
            return jsonify(latest)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/all", methods=["GET"])
def all_results():
    try:
        if not os.path.exists(LOG_FILE):
            return jsonify([])  # No logs yet

        with open(LOG_FILE, "r") as f:
            data = [json.loads(line) for line in f.readlines()]
            return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5001, debug=True)

