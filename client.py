import socket
import sys
import select

class Connection:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect(('127.0.0.1', 50000))
        self.s.send('Yo!'.encode('utf-8'))
    def on_read(self):
        data = self.s.recv(1024).decode('utf-8')
        return data
    def on_write(self, msg):
        self.s.send(msg.encode('utf-8'))
    def fileno(self):
        return self.s.fileno()

class Input:
    def readline(self):
        msg = sys.stdin.readline()
        return msg
    def fileno(self):
        return sys.stdin.fileno()

writer = []
connection = Connection()
input_fd = Input()
writer.append(connection.fileno())
writer.append(input_fd.fileno())

while True:
    print('> ', end='')
    sys.stdout.flush()
    readers, _, _ = select.select(writer, [], [])
    for reader in readers:
        if reader is input_fd.fileno():
            msg = input_fd.readline()
            connection.on_write(msg)

        if reader is connection.fileno():
            msg = connection.on_read()
            print('\b\b', end='')
            print('server >>> %s' % (msg), end='')
