# client
import hashlib
import socket
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(0.1)
host = sys.argv[1]
file = sys.argv[2]
hasher = hashlib.md5()
blksize = 512
wsize = 16
port = (host, 69)

sock.sendto(b'\x00\x01' + bytes(file, "UTF-8") + b'\x00octet\x00windowsize\x00' + bytes(str(wsize), "UTF-8") + b'\x00', port)

i = 0
last = b'\x00\x00'
counter = 0

def send_ack(pack_number):
    sock.sendto(b'\x00\x04' + pack_number, port)

while True:
    error = 0

    try:
        a, b = sock.recvfrom(4096)
    except socket.timeout:
        send_ack((counter).to_bytes(2, byteorder='big'))
        continue

    if a[0:2] == b'\x00\x03':
        if i == 0:
            port = b
            i = 1
            wsize = 1

        if a[2:4] == ((counter + 1) % (2**16)).to_bytes(2, byteorder='big'):
            counter = (counter + 1) % (2**16)
            hasher.update(a[4:])
        else:
            error = 1

        if len(a) < blksize + 4:
            send_ack((counter).to_bytes(2, byteorder='big'))
            break

        if counter%wsize == 0 or error == 1:
            send_ack((counter).to_bytes(2, byteorder='big'))

    if a[0:2] == b'\x00\x06':
        if i == 0:
            port = b
            i = 1

        wsize = int((a).split(b'\x00')[2])
        send_ack(b'\x00\x00')



print(hasher.hexdigest())