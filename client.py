import socket
import sys
import select

class Connection:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect(('127.0.0.1', 50000))
        # self.s.send('Yo!'.encode('utf-8'))
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

class Cursol:
    def __init__(self, cursol):
        self.cursol = cursol
    def print_cursol(self):
        print(self.cursol, end='')
    def clear_cursol(self):
        n = len(self.cursol)
        print('\b' * n, end='')

def recv_parse(data):
    data_stliped = data.split()
    src_name = data_stliped[0]
    msg = ' '.join(data_stliped[1:]) # 2つ目のブランク回避
    return src_name, msg

# def remove_rn(data):
#     data = data[:]
#     return data

writer = []
connection = Connection()
input_fd = Input()
writer.append(connection.fileno())
writer.append(input_fd.fileno())

cursol = Cursol('> ')
while True:
    cursol.print_cursol()
    sys.stdout.flush()
    readers, _, _ = select.select(writer, [], [])
    for reader in readers:
        if reader is input_fd.fileno():
            msg = input_fd.readline()
            connection.on_write(msg)

        if reader is connection.fileno():
            data = connection.on_read()
            name, msg = recv_parse(data)
            cursol.clear_cursol()
            print('[%s] >>> %s' % (name, msg))
