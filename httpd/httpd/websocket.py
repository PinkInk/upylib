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
        pass


    def sendframe(self):
        f = self.conn.makefile(mode="wb")
    
    # TODO: this should move to parse.py 
    #       (or other websocket specific file)
    #       be generalised for client<->server msgs
    #       and return named tuple (from server) or bytes (to client)?
    def recvframe(self):
        frame = self.recv()
        mf = memoryview(frame)
        ptr = 0
        fin = bool( mf[ptr] & (1<<7) )
        # ignore bitfields reserved for future
        opcode = mf[ptr] & 0b1111
        ptr += 1
        use_mask = bool( mf[ptr] & (1<<7) )
        length = mf[ptr] & 0x7f
        if length == 126:
            length = bytes_to_int( mf[ptr+1:ptr+1+2] )
            ptr += 1+2
        elif length == 127:
            length = bytes_to_int( mf[ptr+1:ptr+1+4] )
            ptr += 1+4
        else:
            ptr += 1
        mask = mf[ptr:ptr+4]
        ptr += 4
        # TODO: client to server will always use_mask
        if use_mask:
            # client to server msg
            # TODO : consistency; message should be bytes not str
            msg = "" # what about non text messages?
            for i in range(len(mf[ptr:])):
                msg += chr( mf[ptr+i]^mask[i%4] )
        else:
            # server to client msgs
            msg = mf[ptr:]
        return fin, opcode, msg 
        
    def recv(self):
        b = b""
        while True:
            count = self.conn.readinto( self.buf )
            if count:
                b += self.buf[:count]
            else:
                break
        return b

    def send(self, b):
        if b:
            self.conn.send(b)
