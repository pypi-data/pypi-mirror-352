import socket
import selectors

class UdpTransport:
    def __init__(self, port=0):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', port))
        self.sock.setblocking(False)
        self.port = self.sock.getsockname()[1]

    def send(self, destination, data: bytes):
        self.sock.sendto(data, destination)

    def receive(self, bufsize=8192):
        try:
            data, addr = self.sock.recvfrom(bufsize)
            return data, addr
        except BlockingIOError:
            return None, None

    def get_channel(self):
        return self.sock

    def get_port(self):
        return self.port