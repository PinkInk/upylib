# https://tools.ietf.org/html/rfc6455

try:
    from uhashlib import sha1
except:
    from hashlib import sha1

try:
    from ubinascii import b2a_base64
except:
    from binascii import b2a_base64

try:
    from ucollections import namedtuple
except:
    from collections import namedtuple 

def bytes_to_int(b): #big-endian
    i = 0
    for b8 in b:
        i <<= 8
        i += b8
    return i

Frame = namedtuple("Frame", ("final", "opcode", "msg"))

OP_CONT = 0x0 # continuation frame
OP_TEXT = 0x1 # text frame
OP_BIN = 0x2 # binary frame
OP_CLOSE = 0x8 # close connection
OP_PING = 0x9 # ping frame
OP_PONG = 0xa # pong frame


class WebSocketError(Exception):
    pass


class WebSocket:

    RHEAD = b"HTTP/1.1 101 Switching Protocols\r\n"
    MAGIC = b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

    def __init__(self, request, conn, buflen=128):
        print("bring up websocket ...") # DEBUG
        self.conn = conn
        self._buf = bytearray(buflen)
        self.buf = memoryview(self._buf)

        # negotiate websocket, assumes caller tested is_websocket_request
        self.conn.send( self.RHEAD )
        self.conn.send( b"Upgrade: websocket\r\nConnection: Upgrade" ) 

        key = bytes( request.options["Sec-WebSocket-Key"], "utf-8" )
        key.update( self.MAGIC )
        self.conn.send( b"Sec-WebSocket-Accept: " + b2a_base64(key.digest)[:-1] )

        # client will fail if extensions or protocol don't match request
        if "Sec-Websocket-Extensions" in request.options:
            self.conn.send( 
                b"Sec-WebSocket-Extensions: " + \
                bytes(request.options["Sec-WebSocket-Extensions"], "utf-8") + \
                b"\r\n" 
            )
        if "Sec-WebSocket-Protocol" in request.options:
            self.conn.send(
                b"Sec-WebSocket-Protocol" + \
                bytes(request.options["Sec-WebSocket-Protocol"], "utf-8") + \
                b"\r\n"
            )
        self.conn.send(b"\r\n")

        print("websocket up ...")
    
    def service_frames(self):
        print("starting servicing ...") # DEBUG
        frame = self.recvframe()
        print("received a frame ...", frame) # DEBUG
        if frame:
            if frame.opcode == OP_PING:
                print("send pong ...") # DEBUG
                self.sendframe(OP_PONG, frame.msg)
            elif frame.opcode == OP_PONG:
                pass # ignore

    def sendframe(self, opcode, msg, final=True):
        b = bytes([(final<<7) + opcode ])
        length = len(msg)
        if length < 126:
            b += bytes([length])
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
        # server to client doesn't use mask, concat coerces str msg to bytes
        self.conn.send( b + msg )

    def recvframe(self):
        frame = self.recv()
        if frame:
            mf = memoryview(frame)
            ptr = 0
            final = bool( mf[ptr] & (1<<7) )
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
            if use_mask:
                msg = b""
                # for i in range(len(mf[ptr:])):
                for i in range(length):
                    msg += bytes([ mf[ptr+i]^mask[i%4] ])
                return Frame(final, opcode, msg) 
            else:
                raise WebSocketError("Unmasked client websocket frame")
        
    def recv(self):
        b = b""

        # ??? binary ???

        try: # micropython 
            readline = self.conn.readline
        except AttributeError: # cpython
            f = self.conn.makefile(mode="rb")
            readline = f.readline 

        line = readline()
        while line:
            print(line)
            b += line
            line = readline()

        return b
