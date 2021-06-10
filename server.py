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

clients_name = {}
def broadcast(sender_client=None, msg=''):
    if sender_client == None:
        for c in clients_name.keys():
            c.send(msg.encode('utf-8'))
        return
    # sender_client以外に送る
    for c in clients_name.keys():
        if c is not sender_client:
            c.send(msg.encode('utf-8'))
        else:
            pass

def name_exist(new_name):
    for name in clients_name.values():
        if name == new_name:
            return True
    return False

def handle_client(client):
    addr, port = client.getpeername()
    name = client.recv(1024).decode('utf-8')
    if name_exist(name) == True:
        client.send('server Error: Your name is already exist'.encode('utf-8'))
        client.close()
        return
    clients_name[client] = name
    print('Connected (%s, %s)' % (addr, port))
    while (True):
        msg = client.recv(1024).decode('utf-8')
        if not msg:
            print('Disconnected (%s, %s)' % (addr, port))
            data = '%s Disconnected: %s' % (SERVER_NAME, clients_name.get(client))
            broadcast(msg=data)
            del clients_name[client]
            client.close()
            break
        data = '%s %s' % (clients_name.get(client), msg)
        broadcast(sender_client=client, msg=data)
        print('%s:%sc >> %s' %
                (addr, port, msg), end='')
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
            data = '%s %s' % (SERVER_NAME, msg)
            if connected == False:
                print('client was not connect!')
            else:
                for c in clients_name.keys():
                    c.send(data.encode('utf-8'))

        if reader is listen.fileno():
            client = listen.accept()
            thread = threading.Thread(target=handle_client, args=(client,))
            thread.start()
            connected = True
