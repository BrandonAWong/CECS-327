import socket
from time import sleep

hostname = socket.gethostname()

print(f"[{hostname}] Starting Cluster {hostname.split()[-2]} with 8 containers...")

# INTRA

message = "Hello, Cluster A!"
print(f'[{hostname}] Sending intra-cluster broadcast message: "{message}"')
sleep(3.5) # wait for other containers to await the message

# AF_INET = using IPv4, SOCK_DGRAM = socket will use UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# sets socket options
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

# sends message through the socket, 255.255.255.255 is the destination address
# and that is the broadcast address for IPv4, allows sending messages to all devices
# on local network. 5000 is port, recieving must be listening on port 5000
sock.sendto(message.encode(), ("255.255.255.255", 5000))
sock.close()

# INTER

# wait to send message, wait for all intra stuff to finish for both clusters
sleep(2)
message = "Greetings from Cluster A. Hello Cluster B."

poop_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# send message to other cluster master who will then send it to little children
print(f'[{hostname}] Sending inter-cluster broadcast message: "{message}"')
poop_sock.sendto(message.encode(), ("192.18.0.10", 6000))
poop_sock.close()

