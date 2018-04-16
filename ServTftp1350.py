import socket

import sys
import threading

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#sock.settimeout(0.5)

port = int(sys.argv[1])

dir = sys.argv[2]

adress = ('localhost', port)

sock.bind(adress)


working = False
file = b'\x00'
data = b'\x00'
counter = 1
last = False
client = ('localhost', 6969)

class Server(threading.Thread):
    def __init__(self, _client, datta, _fille):
        super().__init__()
        self._client = _client
        self._data = datta
        self._file = _fille

    def run(self):
        self._data = self._file.read(512)
        first = True
        _last = False
        _counter = 1
        _sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        _sock.settimeout(0.1)
        while True:
            if first != True:
                try:
                    a, b = _sock.recvfrom(4096)
                    #print(a, b)
                except socket.timeout:
                    if len(self._data) >= 512:
                        _sock.sendto(b'\x00\x03' + (_counter).to_bytes(2, byteorder='big') + self._data[:512], self._client)
                    else:
                        _last = True
                        _sock.sendto(b'\x00\x03' + (_counter).to_bytes(2, byteorder='big') + self._data, self._client)

                    continue

            if first == True:
                first = False
                if len(self._data) >= 512:
                    _sock.sendto(b'\x00\x03' + (_counter).to_bytes(2, byteorder='big') + self._data[:512], self._client)
                else:
                    _last = True
                    _sock.sendto(b'\x00\x03' + (_counter).to_bytes(2, byteorder='big') + self._data, self._client)
                continue

            if a[0:2] == b'\x00\x04':
                if a[2:4] == (_counter).to_bytes(2, byteorder='big'):
                    if _last == True:
                        _counter = 1
                        break
                    else:
                        self._data = self._data[512:]
                        self._data = self._file.read(512)
                        _counter = (_counter + 1) % (2 ** 16)

                        if len(self._data) >= 512:
                            _sock.sendto(b'\x00\x03' + (_counter).to_bytes(2, byteorder='big') + self._data[:512], self._client)
                        else:
                            _sock.sendto(b'\x00\x03' + (_counter).to_bytes(2, byteorder='big') + self._data, self._client)
                            _last = True
                else:
                    if len(self._data) >= 512:
                        _sock.sendto(b'\x00\x03' + (_counter).to_bytes(2, byteorder='big') + self._data[:512], self._client)
                    else:
                        _sock.sendto(b'\x00\x03' + (_counter).to_bytes(2, byteorder='big') + self._data, self._client)
                        _last = True

        _sock.close()

while True:
    a, b = sock.recvfrom(4096)

    if a[0:2] == b'\x00\x01':
        file = a.split(b'\x00')[1][1:]
        in_file = open(dir + "/" + file.decode("utf-8"), "rb")
        client = b
        tftpServer = Server(client, data, in_file)
        tftpServer.start()





