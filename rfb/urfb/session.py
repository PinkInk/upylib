from utime import sleep_ms
from ustruct import pack
# from rfb.clientmsgs import dispatch_msgs
# from rfb.servermsgs import ServerSetPixelFormat

class RfbSession():

    # on fail raise; to prevent invalid session at parent
    def __init__(self, conn, w, h, name):
        self.conn, self.addr = conn
        self.w = w
        self.h = h
        self.bpp = 32
        self.depth = 24
        self.big = True
        self.true = True
        channel_mask = 2**(self.depth//3)-1
        self.masks = (channel_mask, channel_mask, channel_mask)
        self.shifts = (16,8,0)
        self.name = name
        self.security = 1 # None/No Security
        self.encodings = [] # sent post init by client

        # HandShake
        self.send( b'RFB 003.003\n' )
        if self.recv(True) != b'RFB 003.003\n':
            raise Exception('RFB rejected version proposal')

        # Security
        self.send( pack('>L', self.security) )
        # ignore instruction to disconnect other clients
        if self.recv(True)[0] not in (0,1):
            raise Exception('RFB rejected no security')

        # ServerInit
        self.send(
            pack('>2H', w, h) \
            + ServerSetPixelFormat(
                self.bpp, self.depth, 
                self.big, self.true,
                self.masks, self.shifts
            ) \
            + pack('>L', len(name)) \
            + name
        )

        # we *may* be sent encodings and pixel format
        self.service_msg_queue()

    def recv(self, blocking=False):
        sleep_ms(100) #init fails at peer without this delay???
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
