from enum import Enum, auto
import socket

class ConnectionManager:

    @staticmethod
    def has_internet(timeout: float = 2.0) -> bool:

        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
            return True
        
        except OSError:
            return False
        
    