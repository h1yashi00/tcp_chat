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

class Clients_name():
    _socks = []
    _names = []
    def add(self, sock, name):
        self._socks.append(sock)
        self._names.append(name)
    def get_name(self, want_sock):
        i = self._socks.index(want_sock)
        return self._names[i]
    def get_sock(self, want_name):
        i = self._names.index(want_name)
        return self._socks[i]
    def name_exist(self, ex_name):
        return ex_name in self._names
    def get_names(self):
        return self._names
    def get_socks(self):
        return self._socks
    def remove(self, sock):
        name = self.get_name(sock)
        self._names.remove(name)
        self._socks.remove(sock)

def check_command(data):
    if data[-1] == '\n':
        print('True')
        data = data[:-1]
    if data == 'connections':
        return ' '.join(clients.get_names())
    else:
        return 'invalid command'

def choice_method(sender, data):
    if data[0] == '@':
        splited_data = data[1:].split()
        name = splited_data[0]
        msg = ' '.join(splited_data[1:])
        if clients.name_exist(name) == False:
            return sender, 'name not exist'
        sender_name = clients.get_name(sender)
        dest_sock = clients.get_sock(name)
        msg = '%s %s' % (sender_name, msg)
        return msg, dest_sock
    elif data[0] == '/':
        msg = check_command(data[1:])
        return msg, None
    else:
        sys.stderr.write('error: occured in choice_method data: %s' % data)
        exit(0)

def broadcast(sender_client=None, msg=''):
    if sender_client == None:
        for c in clients.get_socks():
            c.send(msg.encode('utf-8'))
        return
    # sender_client以外に送る
    for c in clients.get_socks():
        if c is not sender_client:
            c.send(msg.encode('utf-8'))
        else:
            pass

def handle_client(client):
    addr, port = client.getpeername()
    name = client.recv(1024).decode('utf-8')
    if clients.name_exist(name) == True:
        client.send('server Error: Your name is already exist'.encode('utf-8'))
        client.close()
        return
    clients.add(client, name)
    print('Connected (%s, %s)' % (addr, port))
    while (True):
        msg = client.recv(1024).decode('utf-8')
        if not msg:
            print('Disconnected (%s, %s)' % (addr, port))
            data = '%s Disconnected: %s' % (SERVER_NAME, clients.get_name(client))
            broadcast(msg=data)
            clients.remove(client)
            client.close()
            break
        if msg[0] == '@' or msg[0] == '/':
            data, dst_sock = choice_method(client, msg)
            msg = '%s %s' % (SERVER_NAME, data)
            if dst_sock == None:
                client.send(msg.encode('utf-8'))
                print('%s:%sc >> %s' % (addr, port, msg), end='')
            else:
                dst_sock.send(msg.encode('utf-8'))
                print('%s:%sc >> %s' % (addr, port, msg), end='')
        else:
            data = '%s %s' % (clients.get_name(client), msg)
            broadcast(sender_client=client, msg=data)
            print('%s:%sc >> %s' %
                    (addr, port, msg), end='')
            sys.stdout.flush()
            # print('>> ', end='')

SERVER_NAME = 'server'
clients = Clients_name()
writer = []
listen = Create_server_socket('127.0.0.1', 50000)
input_reader = Input()

writer.append(listen.fileno())
writer.append(input_reader.fileno())

while True:
    # select(write, read, sig)
    readers, _, _ = select.select(writer, [], [])
    for reader in readers:
        if reader is input_reader.fileno():
            msg = input_reader.readline()
            data = '%s %s' % (SERVER_NAME, msg)
            if len(clients.get_socks()) == 0:
                print('client was not connect!')
            else:
                for c in clients.get_socks():
                    c.send(data.encode('utf-8'))

        if reader is listen.fileno():
            client = listen.accept()
            thread = threading.Thread(target=handle_client, args=(client,))
            thread.start()
