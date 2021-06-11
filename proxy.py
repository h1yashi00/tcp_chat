import socket
from struct import *
import select

class Proxy():
    def __init__(self, in_address, in_port, out_address, out_port):
        self._in_address  = in_address
        self._in_port     = in_port
        self._out_address = out_address
        self._out_port    = out_port
    def accept(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self._in_address, self._in_port))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        s.listen(5)
        client_sock = s.accept()
        return client_sock[0]
    def connect(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self._out_address, self._out_port))
        return s

p = Proxy('localhost', 25565, 'syuu.net', 25565)
client_proxy = p.accept()
print('debug: %s' % client_proxy)
proxy_server = p.connect()
print('debug: %s' % proxy_server)

# select で識別する必要性がある
while True:
    readers, _, _ = select.select([client_proxy.fileno(), proxy_server.fileno()], [], [])
    for reader in readers:
        if reader is client_proxy.fileno():
            data = client_proxy.recv(1024)
            if not data:
                print('cloned client')
                proxy_server.close()
                client_proxy.close()
                break
            print('->: %s' % data)
            proxy_server.send(data)

        if reader is proxy_server.fileno():
            data = proxy_server.recv(1024)
            if not data:
                print('cloned server')
                proxy_server.close()
                client_proxy.close()
                break
            print('<-: %s' % data)
            client_proxy.send(data)
