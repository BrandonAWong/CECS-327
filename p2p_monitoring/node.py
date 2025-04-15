from flask import Flask, jsonify, request, send_from_directory
from uuid import uuid4
from threading import Thread
from time import sleep
from socket import gethostname
import requests
import logging

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

node_id = str(uuid4())
peers = set()
addr = f"http://{gethostname()}:5000"
kvs = {}
app = Flask(__name__)

@app.route("/", methods=["GET"])
def self_message():
    return jsonify({"message": f"Node {node_id} is running!"}), 200

@app.route("/register", methods=["POST"])
def register_peer():
    data = request.get_json()
    peer = data.get("peer")

    if peer not in peers:
        peers.add(peer)

    return jsonify({"status": "registered"}), 200

@app.route("/message", methods=["POST"])
def receive_message():
    data = request.get_json()
    print(f"Received message from {data.get('sender')}: {data.get('msg')}")
    return jsonify({"status": "received"}), 200

@app.route("/peers", methods=["GET"])
def get_peers():
    return jsonify({"peers": list(peers)}), 200

# File UPLOAD
@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files["file"]
    file.save(f"./storage/{file.filename}")
    return jsonify({"status": f"uploaded {file.filename}", "filename": file.filename}), 201

@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    return send_from_directory("/storage", filename, as_attachment=True)

# Key-Value Store
@app.route("/kv", methods=["POST"])
def add_kv_pair():
    data = request.get_json()
    key = data.get("key")
    value = data.get("value")

    if not key or not value:
        return jsonify({"error": "'key' and 'value' cannot be empty"})

    kvs[key] = value
    return jsonify({"status": f"key pair {key}-{value} added successfully"}), 201

@app.route("/kv/<key>")
def get_kv_value(key):
    res = kvs.get(key)

    if res is not None:
        return jsonify({"value": res})
    else:
        return jsonify({"error": "key not found in storage"})

# THREAD BS DISCOVCERY
def find_peers():
    global peers

    while True:
        if not peers:
            response = requests.get("http://bootstrap:5000/peers")
            peers = set([peer for peer in response.json()["peers"] if peer != addr])
        else:
            tpeer = []

            for peer in peers:
                response = requests.get(f"{peer}/peers")
                tpeer = tpeer + list(response.json()["peers"])

            for peer in set(tpeer):
                if peer not in peers and peer != addr:
                    peers.add(peer)

        sleep(10)


# run node before registering, prevent node from being queried before up
app.run(host="0.0.0.0", threaded=True)

# populate peer list
discover_thread = Thread(target=find_peers, daemon=True)
discover_thread.start()

# register node with bootstrap
requests.post("http://bootstrap:5000/register", json={"peer": addr})

