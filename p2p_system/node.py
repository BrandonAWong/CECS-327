from flask import Flask, jsonify, request
from uuid import uuid4
from threading import Thread
from time import sleep
from socket import gethostname
import requests
import logging
from random import randint

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

node_id = str(uuid4())
peers = set()
addr = f"http://{gethostname()}:5000"
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

def message_peers():
    while True:
        for peer in peers:
            requests.post(f"{peer}/message", json={"sender": gethostname(), 
                                                   "msg": f"SUPSUP YO NODE {peer.split("/")[2].replace(":5000", "")}"})

        sleep(randint(5, 45))

# populate peer list
discover_thread = Thread(target=find_peers, daemon=True)
discover_thread.start()

# register node with bootstrap
requests.post("http://bootstrap:5000/register", json={"peer": addr})

message_thread = Thread(target=message_peers, daemon=True)
message_thread.start()

app.run(host="0.0.0.0")

