# netcrypt/tunnel.py

from .sockets import SecureSocket
import threading

def start_secure_tunnel(mode: str, key: bytes, host: str = 'localhost', port: int = 9000):
    sock = SecureSocket(key, host, port)
    if mode == 'server':
        sock.start_server()
    elif mode == 'client':
        sock.start_client()
    else:
        raise ValueError("Mode must be either 'server' or 'client'")

def start_tunnel_in_thread(mode: str, key: bytes, host: str = 'localhost', port: int = 9000):
    thread = threading.Thread(target=start_secure_tunnel, args=(mode, key, host, port))
    thread.daemon = True
    thread.start()
    return thread
