# https://tools.ietf.org/html/rfc6455

import httpd.parse as parse
from sha1 import sha1

try:
    from ubinascii import *
except:
    from binascii import *

try:
    from ucollections import namedtuple
except:
    from collections import namedtuple 

Frame = namedtuple("Frame", ("final", "opcode", "msg"))

OP_CONT = 0x0 # continuation frame
OP_TEXT = 0x1 # text frame
OP_BIN = 0x2 # binary frame
OP_CLOSE = 0x8 # close connection
OP_PING = 0x9 # ping frame
OP_PONG = 0xa # pong frame

# NOTE: not reqd whilst we are not using, 
#       therefore not decoding, frame length
# micropython int.from_bytes doesn't support big-endian
# def bytes_to_int(b): #big-endian
#     i = 0
#     for b8 in b:
#         i <<= 8
#         i += b8
#     return i

# test http request for parameters required by rfc6455
# indicating request is request to create websocket
def is_websocket_request(request):
    opts = request.options
    if "Sec-WebSocket-Key" in opts \
            and "Upgrade" in opts \
                and opts["Upgrade"] == "websocket" \
            and "Connection" in opts \
                and opts["Connection"] == "Upgrade" \
            and "Sec-WebSocket-Version" in opts \
                and opts["Sec-WebSocket-Version"] == "13" \
            and "Origin" in opts \
            and "Host" in opts \
            and request.ver.major >= 1 \
                and request.ver.minor >= 1:
        return True
    return False


class WebSocketError(Exception):
    pass


class WebSocket:

    MAGIC = b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

    def __init__(self, conn, request, buflen=128):
        self.conn,self.addr = conn
        # TODO: is memoryview waranted?
        self._buf = bytearray(buflen)
        self.buf = memoryview(self._buf)
                
        # negotiate websocket
        # ASSUMES: caller tested is_websocket_request
        options = { "Upgrade": "websocket", "Connection": "Upgrade" }
        options["Sec-WebSocket-Accept"] = \
                b2a_base64(unhexlify(
                    sha1(request.options["Sec-WebSocket-Key"] + self.MAGIC)
                ))[:-1] # skip trailing newline
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
    
    def service_frames(self):
        frame = self.recvframe()
        if frame:
            if frame.opcode == OP_PING:
                self.sendframe(OP_PONG, frame.msg)
            elif frame.opcode == OP_PONG:
                pass # ignore

    def sendframe(self, opcode, msg, final=True):
        # TODO: handling of ping, pending pong?
        b = bytes([(fin<<7) + opcode ])
        length = len(msg)
        if length < 126:
            b += bytes([length]) # bytes([ (use_mask<<7) + length ])
        # TODO : unuglify -->
        elif length <= 0xffff:
            b += bytes([ 0, length>>8, length&0xff ])
        elif 0xffff < length <= 0xffffffff:
            b += bytes([ 0,
                         length>>32,
                         (length&0xff0000)>>16,
                         (length&0xff00)>>8,
                         length&0xff
                      ])
        else:
            raise WebSocketError("Message too long")
        # server to client msgs don't use mask
        # concat converts str msg to bytes
        self.send( b + msg )

    def recvframe(self):
        frame = self.recv()
        if frame:
            mf = memoryview(frame)
            ptr = 0
            final = bool( mf[ptr] & (1<<7) )
            opcode = mf[ptr] & 0b1111
            ptr += 1
            use_mask = bool( mf[ptr] & (1<<7) )
            # TODO: use length in decode-loop
            #       meanwhile don't decode, skip
            length = mf[ptr] & 0x7f
            if length == 126:
                # length = bytes_to_int( mf[ptr+1:ptr+1+2] )
                ptr += 1+2
            elif length == 127:
                # length = bytes_to_int( mf[ptr+1:ptr+1+4] )
                ptr += 1+4
            else:
                ptr += 1
            mask = mf[ptr:ptr+4]
            ptr += 4
            if use_mask:
                msg = b""
                # decode-loop, ignores encoded frame length
                # and assumes balance bytes are encoded msg
                for i in range(len(mf[ptr:])):
                    msg += bytes([ mf[ptr+i]^mask[i%4] ]) # chr( mf[ptr+i]^mask[i%4] )
                return Frame(final, opcode, msg) 
            else:
                raise WebSocketError("Unmasked client websocket frame")
        
    # TODO: test!
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
