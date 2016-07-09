from utime import sleep_ms
from ustruct import pack
from messages import *

class RfbSession():

    # on fail raise; to prevent invalid session at parent
    def __init__(self, conn, w, h, name):
        self.conn = conn[0]
        self.w = w
        self.h = h
        self.bpp = 32
        self.depth = 24
        self.big = True
        self.true = True
        self.masks = (255, 255, 255)
        self.shifts = (16,8,0)

        # HandShake
        self.send( b'RFB 003.003\n' )
        if self.recv(True) != b'RFB 003.003\n':
            raise Exception('RFB rejected version proposal')

        # Security
        self.send( b'\x00\x00\x00\x01' )
        # ignore instruction to disconnect other clients
        if self.recv(True)[0] not in (0,1):
            raise Exception('RFB rejected security none')

        # ServerInit
        self.send(
            + pack('>2H4B3H3B',
                w, h, 
                self.bpp, self.depth, self.big, self.true,
                masks[0], masks[0], masks[0],
                shifts[0], shifts[1], shifts[2]
            ) \
            + bytes(3) \ 
            + pack('>L', len(name)) \
            + name
        )

        # we *may* be sent encodings (ignorred) and pixel format
        self.service_msg_queue()

    def recv(self, blocking=False):
        while blocking:
            sleep_ms(100)
            r = self.conn.recv(1024)
            if r is not None:
                return r
        try:
            sleep(1)
            return self.conn.recv(1024)
        except:
            pass

    def send(self, b):
        if b: # None and b'' are False
            self.conn.send(b)

    def service_msg_queue(self):
        msg = self.recv()
        if msg == b'': #closed by peer
            return False
        elif msg is not None:
            dispatch_msgs(self, msg)
        return True