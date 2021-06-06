import socket
import sys
import select

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 50000))

while True:
    print('> ', end='')
    sys.stdout.flush()
    readers, _, _ = select.select([sys.stdin.fileno(), s.fileno()], [], [])
    for reader in readers:
        if reader is sys.stdin.fileno():
            msg = sys.stdin.readline().encode('utf-8')
            s.send(msg)

        if reader is s.fileno():
            data = s.recv(1024)
            print('\b\b', end='')
            print('server >>> %s' % (data.decode('utf-8')), end='')
