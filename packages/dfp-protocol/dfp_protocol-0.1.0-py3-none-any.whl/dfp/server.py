import socket
import threading
from .protocol import decode_message
from .flags import FLAGS

class DFPServer:
    def __init__(self, host="0.0.0.0", port=9000):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):
        self.server.bind((self.host, self.port))
        self.server.listen()
        print(f"[DFPServer] Listening on {self.host}:{self.port}")
        while True:
            client, addr = self.server.accept()
            print(f"[DFPServer] Connected by {addr}")
            threading.Thread(target=self.handle_client, args=(client,)).start()

    def handle_client(self, client):
        with client:
            while True:
                data = client.recv(1024)
                if not data:
                    break
                flag, payload = decode_message(data)
                if flag not in FLAGS:
                    client.sendall(f"ERR | Unsupported flag {flag}".encode("utf-8"))
                    continue
                print(f"[DFPServer] {flag=} {payload=}")
                client.sendall(f"ACK|{flag}".encode("utf-8"))
