import httpd.parse as parse
from sha1 import sha1
from binascii import *

def bytes_to_int(b): #big-endian
    i = 0
    for b8 in b:
        i <<= 8
        i += b8
    return i


class WebSocket:

    MAGIC = b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    RESPONSE = b"HTTP/1.x 101 Switching Protocols\r\n"

    def __init__(self, conn, request, buflen=128):
        self.conn,self.addr = conn
        self.buf = memoryview(bytearray(buflen))
                
        options = { "Upgrade": "websocket", "Connection": "Upgrade" }
        options["Sec-WebSocket-Accept"] = \
                b2a_base64(unhexlify(
                    sha1(request.options["Sec-WebSocket-Key"] + self.MAGIC)
                ))[:-1]
        # client will fail negotation if extensions 
        # or protocol don't match the  request
        if "Sec-Websocket-Extensions" in request.options:
            options["Sec-WebSocket-Extensions"] = \
                request.options["Sec-WebSocket-Extensions"]
        if "Sec-WebSocket-Protocol" in request.options:
            options["Sec-WebSocket-Protocol"] = \
                bytes(request.options["Sec-WebSocket-Protocol"]
        
        self.send("HTTP/1.x 101 Switching Protocols\r\n")
        for key in options:
            self.send(
                bytes(key, "utf-8") + b":" \
                + bytes(options[key], "utf-8") + b"\r\n"
            )
        self.send(b"\r\n")
    
    def service_requests(self):
        


    def sendframe(self):
        f = self.conn.makefile(mode="wb")
    
    def recvframe(self):
        f = self.conn.makefile(mode="rb")


    def recv(self, count=1024, blocking=False):
        while blocking:
            r = self.conn.recv(count)
            if r is not None:
                return r
        try:
            return self.conn.recv(count)
        except:
            pass

    def send(self, b):
        if b:
            self.conn.send(b)
