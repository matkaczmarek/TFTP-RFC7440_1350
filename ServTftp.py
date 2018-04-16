import socket
import struct
import sys
import threading

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

port = int(sys.argv[1])
dir = sys.argv[2]

adress = ('localhost', port)
sock.bind(adress)

working = False
file = b'\x00'
data = b'\x00'
counter = 1
last = False
client = ('localhost', 69)


class Server(threading.Thread):
    def __init__(self, _client, datta, _fille, options, wsize):
        super().__init__()
        self._client = _client
        self._data = []
        self._file = _fille
        self._last = False
        self._wsize = wsize
        self._options = options
        self.blksize = 512
        self._counter = 0

    def load_file(self):
        self._data = [(0,0)]

        _counter = 1
        tmp = self._file.read(self.blksize)

        while len(tmp) > 0:
            self._data.append((_counter, tmp))
            _counter += 1
            tmp = self._file.read(self.blksize)

        self._data.append((_counter, b''))

        self._file.close()

    def send_data(self, _sock, _counter):
        if len(self._data[_counter][1]) >= self.blksize:
            _sock.sendto(b'\x00\x03' + (_counter).to_bytes(2, byteorder='big') + self._data[_counter][1], self._client)
        else:
            _last = True
            _sock.sendto(b'\x00\x03' + (_counter).to_bytes(2, byteorder='big') + self._data[_counter][1], self._client)
            self._last = True

    def send_window(self, _sock, _counter):
        _counter += 1
        end = min(_counter + self._wsize, len(self._data))

        for i in range(_counter , end):
            self.send_data(_sock, i)


    def run(self):
        print("SENDING STARTED")
        self.load_file()
        first = True
        self._last = False
        _counter = 0
        if self._options == False:
            _counter = 1
        _sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        _sock.settimeout(0.1)
        while True:
            if first != True:
                try:
                    a, b = _sock.recvfrom(4096)
                except socket.timeout:
                    self.send_window(_sock, _counter)
                    continue

            if first:
                first = False
                if self._options:
                    _sock.sendto(b'\x00\x06windowsize\x00' + bytes(str(self._wsize), "UTF-8") + b'\x00', self._client)
                else:
                    self.send_data(_sock, _counter)
                continue

            if a[0:2] == b'\x00\x04':
                number = struct.unpack("!H", a[2:4])[0]

                if number >= _counter:
                    _counter = number
                    if self._last:
                        break
                    else:
                        self.send_window(_sock, _counter)
                else:
                    self.send_data(_sock, _counter)


        print("SENDING END")
        _sock.close()


while True:
    a, b = sock.recvfrom(4096)

    if a[0:2] == b'\x00\x01':
        print("REQUEST FROM ", b)
        file = a.split(b'\x00')[1][1:]
        in_file = open(dir + "/" + file.decode("utf-8"), "rb")
        client = b
        if (len(a.split(b'\x00')) > 4):
            tftpServer = Server(client, data, in_file, True, int((a).split(b'\x00')[4]))
        else:
            tftpServer = Server(client, data, in_file, False, 1)

        tftpServer.start()
