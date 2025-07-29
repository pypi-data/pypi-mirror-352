# netcrypt/sockets.py

import socket
from .encryptors import AESCipher

class SecureSocket:
    def __init__(self, key: bytes, host='localhost', port=9000):
        self.key = key
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.aes = AESCipher(self.key)

    def start_server(self):
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)
        print(f"[+] Secure server listening on {self.host}:{self.port}")
        conn, addr = self.sock.accept()
        print(f"[+] Connection from {addr}")
        while True:
            data = conn.recv(4096)
            if not data:
                break
            decrypted = self.aes.decrypt(data)
            print(f"[Received]: {decrypted.decode()}")
        conn.close()

    def start_client(self):
        self.sock.connect((self.host, self.port))
        print(f"[+] Connected to {self.host}:{self.port}")
        try:
            while True:
                msg = input("Send: ").encode()
                encrypted = self.aes.encrypt(msg)
                self.sock.sendall(encrypted)
        except KeyboardInterrupt:
            print("\n[!] Connection closed")
            self.sock.close()
