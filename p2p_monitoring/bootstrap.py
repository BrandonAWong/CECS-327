from flask import Flask, request, jsonify, render_template
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

peers = set()
logs = []
app = Flask(__name__)

@app.route("/register", methods=["POST"])
def register_peer():
    data = request.get_json()
    peer = data.get("peer")

    if peer not in peers:
        peers.add(peer)

    logs.append((f"{peer} registered", datetime.now(ZoneInfo("America/Los_Angeles"))))
    return jsonify({"message": "Peer registered successfully"}), 200

@app.route("/unregister", methods=["POST"])
def unregister_peer():
    data = request.get_json()
    peer = data.get("peer")

    if peer in peers:
        peers.remove(peer)

    logs.append((f"{peer} unregistered", datetime.now(ZoneInfo("America/Los_Angeles"))))
    return jsonify({"message": "Peer unregistered successfully"}), 200

@app.route("/peers", methods=["GET"])
def get_peers():
    return jsonify({"peers": list(peers)}), 200

@app.route("/logs", methods=["POST"])
def create_log():
    data = request.get_json()
    message = data.get("message")
    logs.append((message, datetime.now(ZoneInfo("America/Los_Angeles"))))
    return jsonify({"message": f"'{message}' added to logs"})

@app.route("/logs", methods=["GET"])
def get_logs():
    return jsonify({"logs": logs}), 200

# monitoring front end
@app.route("/")
def home():
    return render_template("index.html", start_time=datetime.now(timezone.utc))

app.run(host="0.0.0.0", threaded=True)
