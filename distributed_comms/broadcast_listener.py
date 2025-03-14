import socket

hostname = socket.gethostname()

# AF_INET = IPv4, SOCK_DRAM = UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# set socket options
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
# binds socket to port 5000 and listen on it
sock.bind(("", 5000))

# receive data from socket, 1024 is max bytes to accept
data, _ = sock.recvfrom(1024)
print(f'[{hostname}] Received broadcast message: "{data.decode()}"')

sock.close()
