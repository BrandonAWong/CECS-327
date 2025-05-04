from flask import Flask, jsonify, request, send_from_directory
from hashlib import sha1
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
    requests.post("http://bootstrap:5000/logs", json={"message": f"{file.filename} uploaded"})
    return jsonify({"status": f"uploaded {file.filename}", "filename": file.filename}), 201

@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    requests.post("http://bootstrap:5000/logs", json={"message": f"{filename} downloaded"})
    return send_from_directory("/storage", filename, as_attachment=True)

# Key-Value Store
@app.route("/kv", methods=["POST"])
def add_kv_pair():
    data = request.get_json()
    key = data.get("key")
    value = data.get("value")
    responsible_node = hash_key_to_node(key)

    print(f"""
          ==========================================
          Saving {key}: {value} at {responsible_node if responsible_node != addr else "self"}
          ==========================================
          """)

    requests.post("http://bootstrap:5000/logs", json={"message": f"Saving {key}: {value} at {responsible_node if responsible_node != addr else "self"}"})

    if addr != responsible_node:
        response = requests.post(f"{responsible_node}/kv", json={"key": key, "value": value})
        return jsonify(response.json())
    else:
        if not key or not value:
            return jsonify({"error": "'key' and 'value' cannot be empty"})

        kvs[key] = value
        return jsonify({"status": f"key pair {key}-{value} added successfully"}), 201

@app.route("/kv/<key>")
def get_kv_value(key):
    responsible_node = hash_key_to_node(key)

    print(f"""
          ==========================================
          Retrieving '{key}' from {responsible_node if responsible_node != addr else "self"}
          ==========================================
          """)

    requests.post("http://bootstrap:5000/logs", json={"message": f"Retrieving '{key}' from {responsible_node if responsible_node != addr else "self"}"})

    if addr != responsible_node:
        response = requests.get(f"{responsible_node}/kv/{key}")
        return jsonify(response.json())
    else:
        res = kvs.get(key)

        if res is not None:
            return jsonify({"value": res})
        else:
            return jsonify({"error": "key not found in storage"})

@app.route("/find-closest/<key>", methods=["GET"])
def find_closest_node(key):
    return jsonify({"node": hash_key_to_node(key, request.args.get("hop"))})

@app.route("/kys", methods=["POST"])
def killself():
    requests.post(f"http://bootstrap:5000/unregister", json={"peer": addr})
    print("""
          ======
          Killed
          ======
          """)
    exit()

def hash_key_to_node(key, hop=0):
    hashed_key = sha1_hash(key)
    peer_distances = {peer: sha1_hash(peer) ^ hashed_key for peer in peers}
    shortest_node = addr

    for _ in range(3):
        if peer_distances and int(hop) < 5:
            node = min(peer_distances, key=peer_distances.get)

            try:
                response = requests.get(f"{node}/find-closest/{key}?hop={int(hop)+1}")
                json = response.json()
            except:
                # peer no longer responding
                peers.remove(node)

            peer_distances.pop(node)

            if sha1_hash(json["node"]) ^ hashed_key <= sha1_hash(shortest_node) ^ hashed_key:
                shortest_node = json["node"]
        else:
            break

    if sha1_hash(shortest_node) ^ hashed_key >= sha1_hash(addr) ^ hashed_key:
        return addr
    else:
        return shortest_node

def sha1_hash(string):
    return int(sha1(string.encode()).hexdigest(), 16)

# THREAD BS DISCOVCERY
def find_peers():
    global peers

    while True:
        if not peers:
            try:
                response = requests.get("http://bootstrap:5000/peers")
                peers = set([peer for peer in response.json()["peers"] if peer != addr])
            except:
                pass
        else:
            tpeer = []

            for peer in peers:
                try:
                    response = requests.get(f"{peer}/peers")
                    tpeer = tpeer + list(response.json()["peers"])
                except:
                    pass

            for peer in set(tpeer):
                if peer not in peers and peer != addr:
                    peers.add(peer)

        sleep(10)



# populate peer list
discover_thread = Thread(target=find_peers, daemon=True)
discover_thread.start()

# register node with bootstrap
response = requests.post("http://bootstrap:5000/register", json={"peer": addr})

app.run(host="0.0.0.0", threaded=True)
