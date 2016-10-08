from utime import sleep_ms
# from time import sleep
# def sleep_ms(t):
#     sleep(t/1000)
from ustruct import pack
# from struct import pack
from urfb.clientmsgs import *

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
        self.send( b'\x00\x00\x00\x01'  )

        # ignore instruction to disconnect other clients
        if self.recv(True)[0] not in (0,1):
            print('2b')
            raise Exception('RFB rejected security none')

        # ServerInit
        self.send(
            pack('>2H4B3H3B',
                w, h, 
                self.bpp, self.depth, self.big, self.true,
                self.masks[0], self.masks[0], self.masks[0],
                self.shifts[0], self.shifts[1], self.shifts[2]
            ) \
            + bytes(3) \
            + pack('>L', len(name)) \
            + name
        )

        # we *may* be sent encodings (ignorred) and pixel format
        self.service_msg_queue()

    def recv(self, blocking=False):
        while blocking:
            sleep_ms(200)
            r = self.conn.recv(1024)
            if r is not None:
                return r
        try:
            sleep_ms(35)
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

def ServerFrameBufferUpdate(rectangles):
    if rectangles: # empty list is False
        buffer = bytes()
        for idx,rect in enumerate( rectangles ):
            b = rect.to_bytes()
            if b is None: # done with this rectangle
                del( rectangles[idx] ) 
            elif b is False:
                pass # no update required
            else:
                buffer += b
        return b'\x00\x00' \
                + pack('>H', len(rectangles)) \
                + buffer
