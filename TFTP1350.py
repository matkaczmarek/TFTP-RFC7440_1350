# client

import hashlib

import socket

import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.settimeout(0.1)

host = sys.argv[1]

file = sys.argv[2]

hasher = hashlib.md5()

port = (host, 6969)

sock.sendto(b'\x00\x01' + bytes(file, "UTF-8") + b'\x00octet\x00', port)

i = 0
last = b'\x00\x00'

while True:

    try:
        a, b = sock.recvfrom(4096)
    except socket.timeout:
        sock.sendto(b'\x00\x04' + last, port)
        continue


    if a[0:2] == b'\x00\x03':

        hasher.update(a[4:])

        if i == 0:
            port = b

            i = 1

        sock.sendto(b'\x00\x04' + a[2:4], port)

        if len(a) < 516:
            break

        last = a[2:4]

print(hasher.hexdigest())