try:
    from utime import sleep
except:
    from time import sleep

try:
    from ustruct import pack
except:
    from struct import pack

from rfb.clientmsgs import dispatch_msgs
from rfb.servermsgs import ServerSetPixelFormat

class RfbSession():

    # on fail raise; to prevent invalid session at parent
    def __init__(self, conn, w, h, name):
        self.conn, self.addr = conn
        self.w = w
        self.h = h
        self.big = True
        self.bpp = 32
        self.depth = 24
        self.true = True
        self.shifts = (16,8,0)
        channel_mask = 2**(self.depth//3)-1
        self.masks = (channel_mask, channel_mask, channel_mask)
        self.name = name
        self._security = 1 # None/No Security
        self.encodings = [] # sent post init by client

        # HandShake
        self.send( b'RFB 003.003\n' )
        if self.recv(True) != b'RFB 003.003\n':
            raise RfbSessionRejected('version proposal')

        # Security
        self.send( pack('>L', self.security) )
        # ignore instruction to disconnect other clients
        if self.recv(True)[0] not in (0,1):
            raise RfbSessionRejected('no security')

        # ServerInit
        self.send(
            pack('>2H', w, h) \
            + ServerSetPixelFormat(
                self.bpp, self.depth, self.big, self.true,
                self.masks, self.shifts
            ) \
            + pack('>L', len(name)) \
            + name
        )
    
    @property
    def security(self):
        return self._security

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

    def service_msg_queue(self):
        msg = self.recv()

        if msg == b'': #closed by peer
            return False

        elif msg is not None:

            dispatch_msgs(self, msg)

        return True


class RfbSessionRejected(Exception):
    pass
