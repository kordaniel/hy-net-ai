import socket
import sys
import struct
import json

HOST = "127.0.0.1"
PORT = 56789


def read_file():
    with open(sys.argv[1], mode='rb') as f:
        return f.read()

bytes = read_file()
jsonheader = {
    "byteorder": sys.byteorder,
    "content-type": "binary/flac",
    "content-encoding": "flac",
    "content-length": len(bytes),
}
jsonheader_bytes = json.dumps(jsonheader, ensure_ascii=False).encode("utf8")
hdr = struct.pack(">H", len(jsonheader_bytes))


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.send(hdr + jsonheader_bytes + bytes)
    data = s.recv(1024)
    while data:
        print(data)
        data = s.recv(1024)
        print("Response:", data)
