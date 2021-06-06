import socket
import select
import sys
import threading

class Create_server_socket():
    def __init__(self, address, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((address, port))
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.s.listen(5)

    def fileno(self):
        return self.s

    def accept(self):
        client = self.s.accept()
        return client[0]

class Input():
    def fileno(self):
        return sys.stdin.fileno()

def handle_client(client):
    print('Now handling %s' % (client))
    while (True):
        msg = client.recv(1024)
        if msg is None:
            break
        else:
            print('client: %s' % ( msg.decode('utf-8') ), end='')
            sys.stdout.flush()

writer = []
clients = []
listen = Create_server_socket('127.0.0.1', 50000)
input_reader = Input()

writer.append(listen.fileno())
writer.append(input_reader.fileno())

connected = False
while True:
    # select(write, read, sig)
    readers, _, _ = select.select(writer, [], [])
    for reader in readers:
        if reader is input_reader.fileno():
            msg = sys.stdin.readline().encode('utf-8')
            if connected == False:
                print('client was not connect!')
            else:
                for c in clients:
                    c.send(msg)

        if reader is listen.fileno():
            client = listen.accept()
            clients.append(client)
            thread = threading.Thread(target=handle_client, args=(client,))
            thread.start()
            connected = True
            # print('client connected by %' % ( clients ))

