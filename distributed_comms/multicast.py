import socket
from time import sleep

hostname = socket.gethostname()

print(f"[{hostname}] Starting Cluster {hostname.split()[-2]} with 8 containers...")

# multicast address to send message to
multicast_group = "224.1.1.1"
message = "Hello, Group B!"
print(f'[{hostname}] Sending intra-cluster multicast message: "{message}"')
sleep(3.5) # wait for other containers to await the message

# af_inet = ipv4, sock_dgram = UDP, ipproto_udp = furhter specify udp 
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

# socket options
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

# send message only to those with the multicast address at port 5007
sock.sendto(message.encode(), (multicast_group, 5007))

