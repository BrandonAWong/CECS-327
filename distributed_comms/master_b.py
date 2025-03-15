import socket
from time import sleep

hostname = socket.gethostname()

print(f"[{hostname}] Starting Cluster {hostname.split()[-2]} with 8 containers...")

# INTRA

# multicast address to send message to
multicast_group = "224.1.1.1"
message = "Hello, Group B!"
print(f'[{hostname}] Sending intra-cluster multicast message: "{message}"')
sleep(3.5) # wait for other containers to await the message

# af_inet = ipv4, sock_dgram = UDP, ipproto_udp = furhter specify udp
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

# socket options
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
sock.settimeout(10)

# send message only to those with the multicast address at port 5007
sock.sendto(message.encode(), (multicast_group, 5007))
sock.close()

# INTER

# recieve from cluster A
poop_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
poop_sock.bind(("", 6000))

data, _ = poop_sock.recvfrom(1024)
message = data.decode()
print(f"[{hostname}] Receieved communication from Cluster A. Sending broacast message: {message}")
poop_sock.close()

# broadcast data from cluster A into cluster B children
nsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
nsock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
nsock.sendto(message.encode(), ("255.255.255.255", 6001))
nsock.close()

