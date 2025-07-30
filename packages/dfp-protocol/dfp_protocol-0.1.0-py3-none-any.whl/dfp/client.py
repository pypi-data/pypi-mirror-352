import socket
from .protocol import encode_message
from .flags import FLAGS

class DFPClient:
    def __init__(self, host="localhost", port=9000):
        
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.client.connect((self.host, self.port))

    def send(self, flag: str, payload: str):
        if flag not in FLAGS:
            raise ValueError(f"[DFP Client] Invalid flag : {flag}") 
    
        message = encode_message(flag, payload)
        self.client.sendall(message)
        return self.client.recv(1024).decode("utf-8")
