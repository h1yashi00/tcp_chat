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
    def readline(self):
        return sys.stdin.readline()


clients = []
# ブロードキャストできるようにする
# client
def broadcast(sender_client, msg):
    for c in clients:
        # sender_client以外に送る
        if c is not sender_client:
            c.send(msg)
        else:
            pass

def handle_client(client):
    # print('Now handling %s' % (client))
    addr, port = client.getpeername()
    print('Connected (%s, %s)' % (addr, port))
    while (True):
        msg = client.recv(1024)
        if msg is None:
            break
        else:
            broadcast(client, msg)
            print('%s:%sc >> %s' %
                    ( addr ,port, msg.decode('utf-8')), end='')
            sys.stdout.flush()
            print('>> ', end='')

SERVER_NAME = 'server'
writer = []
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
            msg = input_reader.readline()
            if connected == False:
                print('client was not connect!')
            else:
                for c in clients:
                    data = '%s %s' % (SERVER_NAME, msg)
                    c.send(data.encode('utf-8'))

        if reader is listen.fileno():
            client = listen.accept()
            clients.append(client)
            thread = threading.Thread(target=handle_client, args=(client,))
            thread.start()
            connected = True
            # print('client connected by %' % ( clients ))

