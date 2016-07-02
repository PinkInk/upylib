try:
    from utime import sleep
    from ustruct import pack
except:
    from time import sleep
    from struct import pack
from rfb.servermsgs import ServerSetColourMapEntries
from rfb.utils import *

class RfbSession():

    # on fail raise; to prevent invalid session at parent
    def __init__(self, conn, w, h, colourmap, name):
        self.conn, self.addr = conn
        self.w = w
        self.h = h
        self.colourmap = colourmap
        # TODO: currently colour = (b,g,r) instead (r,g,b)
        self.big = True
        # TODO: colourmap's don't work ...
        self.bpp = 8 if colourmap else 32
        self.depth = 8 if colourmap else 24
        self.true = False if colourmap else True
        self.shift = (0,0,0) if colourmap else (0,8,16)
        self.name = name
        self.security = 1 # None/No Security
        self.encodings = []

        # HandShake
        self.send( b'RFB 003.003\n' )
        if self.recv(True) != b'RFB 003.003\n':
            raise RfbSessionRejected('version proposal')

        # Security
        self.send( pack('>L', self.security) )
        if self.recv(True)[0] not in (0,1):
            raise RfbSessionRejected('no security')

        # ServerInit
        channel_mask = (2**(self.depth//3)-1 if self.true else 0) 
        self.send(
            pack('>2H4B3H3B',
                 w, h, 
                 self.bpp, self.depth, self.big, self.true,
                 channel_mask, channel_mask, channel_mask,
                 self.shift[0], self.shift[1], self.shift[2]
            ) + bytes(3) + pack('>L', len(name)) + name
        )

        # ColourMap (optional)
        if colourmap:
            self.send( ServerSetColourMapEntries( self.colourmap ) )

    def recv(self, blocking=False):
        sleep(0.1) #init fails at peer without this delay???
        while blocking:
            r = self.conn.recv(1024)
            if r is not None:
                return r
        try:
            return self.conn.recv(1024)
        except:
            pass

    def send(self, b):
        if b: # None and b'' are False
            self.conn.send(b)

    # over-ride to send remote framebuffer updates
    def update(self):
        pass

    def dispatch_msgs(self):
        msg = self.recv()

        if msg == b'': #closed by peer
            return False

        elif msg is not None:

            # handle multiple messages
            ptr = 0
            while ptr < len(msg):

                # ClientSetPixelFormat(self, bpp, depth, big, true, masks, shifts)
                if msg[ptr] == 0:
                    if hasattr(self, 'ClientSetPixelFormat'):
                        self.ClientSetPixelFormat(
                            msg[ptr+4],
                            msg[ptr+5],
                            msg[ptr+6] == 1,
                            msg[ptr+7] == 1,
                            (
                                bytes_to_int( msg[ptr+8:ptr+10] ),
                                bytes_to_int( msg[ptr+10:ptr+12] ),
                                bytes_to_int( msg[ptr+12:ptr+14] ),
                            ),
                            (
                                msg[ptr+14],
                                msg[ptr+15],
                                msg[ptr+16]
                            )
                        )
                    ptr += 20 # includes trailing padding

                # ClientSetEncodings(self, encodings)
                elif msg[ptr] == 2:
                    count = bytes_to_int( msg[ptr+2:ptr+4] )
                    encodings = [
                        bytes_to_int( msg[ptr+4+i : ptr+8+i] )
                        for i in range(0, count*4, 4)
                    ]
                    self.encodings = encodings
                    if hasattr(self, 'ClientSetEncodings'):
                        self.ClientSetEncodings(encodings)
                    ptr += 4 + (count*4)

                # ClientFrameBufferUpdateRequest(self, incr, x, y, w, h)
                elif msg[ptr] == 3:
                    if hasattr(self, 'ClientFrameBufferUpdateRequest'):
                        self.ClientFrameBufferUpdateRequest(
                            msg[ptr+1] == 1,
                            bytes_to_int( msg[ptr+2:ptr+4] ),
                            bytes_to_int( msg[ptr+4:ptr+6] ),
                            bytes_to_int( msg[ptr+6:ptr+8] ),
                            bytes_to_int( msg[ptr+8:ptr+10] )
                        )
                    ptr += 10

                # ClientKeyEvent(self, down, key)
                elif msg[ptr] == 4:
                    if hasattr(self, 'ClientKeyEvent'):
                        self.ClientKeyEvent(
                            msg[ptr+1] == 1,
                            bytes_to_int( msg[ptr+4:ptr+8] )
                        )
                    ptr += 8

                # ClientPointerEvent(self, buttons, x, y)
                elif msg[ptr] == 5:
                    if hasattr(self, 'ClientPointerEvent'):
                        self.ClientPointerEvent(
                            msg[ptr+1],
                            bytes_to_int( msg[ptr+2:ptr+4] ),
                            bytes_to_int( msg[ptr+4:ptr+6] )
                        )
                    ptr += 6

                # ClientCutText(self, text)
                elif msg[ptr] == 6:
                    l = bytes_to_int( msg[2:6] )
                    if hasattr(self, 'ClientCutText'):
                        self.ClientCutText(
                            msg[ptr+6 : ptr+l]
                        )
                    ptr += 6 + len

                elif msg[ptr] > 6 and hasattr(self, 'ClientOtherMsg'):
                    # skip all messages
                    # ... no way to tell how long the msg is ... 
                	ptr = len(msg)

        return True


class RfbSessionRejected(Exception):
    pass
