from flask import Flask, request, jsonify

peers = set()
app = Flask(__name__)

@app.route("/register", methods=["POST"])
def register_peer():
    data = request.get_json()
    peer = data.get("peer")

    if peer not in peers:
        peers.add(peer)

    return jsonify({"message": "Peer registered successfully"}), 200

@app.route("/peers", methods=["GET"])
def get_peers():
    return jsonify({"peers": list(peers)}), 200

app.run(host="0.0.0.0", threaded=True)
