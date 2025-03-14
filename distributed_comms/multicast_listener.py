import socket
import struct
import os

multicast_group = os.getenv("MULTICAST_GROUP", "224.1.1.2")

#INTRA 

# use ipv4 and udp
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
# these options let the port be used by other applications
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# listen on port 5007
sock.bind(("", 5007))

# lets socket join a multicast group
mreq = struct.pack("4sl", socket.inet_aton(multicast_group), socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
sock.settimeout(5)

# listen and wait for data on socket
try:
    data, _ = sock.recvfrom(1024)
    print(f'[{socket.gethostname()}] Received multicast message: "{data.decode()}"')
except:
    pass
sock.close()

# INTER

# RECEIEVED MSG
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.bind(("", 6001))
data, _ = sock.recvfrom(1024)
print(f'[{socket.gethostname()}] Received inter-broadcast message: "{data.decode()}"')
sock.close()
