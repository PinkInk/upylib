from rfb.codecs import *
from time import sleep


class RfbSession():

    # on fails raise; so session not added to svr.sessions
    def __init__(self, conn, w, h, colourmap, name):
        self.conn, self.addr = conn
        self.w = w
        self.h = h
        self.colourmap = colourmap
        self.big = True
        self.bpp = 8 if colourmap else 32
        self.depth = 8 if colourmap else 24
        self.true = False if colourmap else True
        self.rgbshift = (0,0,0) if colourmap else (0,8,16)
        self.name = name
        self.security = 1 # None/No Security
        self.encodings = []

        # HandShake
        self.send( b'RFB 003.003\n' )
        if self.recv(True) != b'RFB 003.003\n':
            raise Exception('Client did not accept version proposal')

        # Security
        self.send( self.security.to_bytes(4, 'big'))
        if self.recv(True)[0] not in (0,1):
            raise Exception('Client rejected security (None)')

        # ServerInit
        self.send(
            w.to_bytes(2, 'big') + h.to_bytes(2, 'big') \
            + bytes([ self.bpp ]) \
            + bytes([ self.depth ]) \
            + bytes([ self.big ]) \
            + bytes([ self.true ]) \
            + (2**(self.depth//3)-1 if self.true else 0).to_bytes(2, 'big') * 3 \
            + bytes( self.rgbshift ) \
            + bytes(3) \
            + len(name).to_bytes(4, 'big') + name
        )

        # ColourMap (optional)
        if colourmap:
            self.send( ServerSetColourMapEntries( self.colourmap ) )

    def recv(self, blocking=False):
        # ??? init fails at peer side without delay ???
        sleep(0.1)
        while blocking:
            # TODO: wrap in try/except as for non-blocking?
            # OR: replace loop by settimeout wrapper?
            r = self.conn.recv(1024)
            if r is not None:
                return r
        try:
            return self.conn.recv(1024)
        except:
            pass

    def send(self, b):
        # print(b) # DEBUG
        self.conn.send(b)

    def dispatch_msgs(self):
        msg = self.recv()

        if msg == b'': #closed by peer
            return False

        elif msg is not None:

            # TODO: handle multiple msgs in queue 

            if msg[0] == 1: # SetPixelFormat
                self.ClientSetPixelFormat(
                    msg[2],
                    msg[3],
                    msg[4] == 1,
                    msg[5] == 1,
                    int.from_bytes(msg[6:8], 'big'),
                    int.from_bytes(msg[8:10], 'big'),
                    int.from_bytes(msg[10:12], 'big'),
                    msg[12],
                    msg[13],
                    msg[14]
                )

            elif msg[0] == 2: # SetEncodings
                # TODO: consider list-comprehension?
                encodings = []
                for i in range( int.from_bytes(msg[2:4], 'big') ):
                    encodings.append(
                        # ??? this bugs-out micropython allocating
                        # unreasonable amounts of memory ??? 
                        int.from_bytes(msg[4+(i*4) : 8+(i*4)], 'big') 
                    )
                self.encodings = encodings
                self.ClientSetEncodings(encodings)

            elif msg[0] == 3: # FrameBufferUpdateRequest
                self.ClientFrameBufferUpdateRequest(
                    msg[1] == 1,
                    int.from_bytes(msg[2:4], 'big'),
                    int.from_bytes(msg[4:6], 'big'),
                    int.from_bytes(msg[6:8], 'big'),
                    int.from_bytes(msg[8:10], 'big'),
                )

            elif msg[0] == 4: # KeyEvent
                self.ClientKeyEvent(
                    msg[1] == 1,
                    int.from_bytes(msg[4:8], 'big')
                )

            elif msg[0] == 5: # PointerEvent
                self.ClientPointerEvent(
                    msg[1],
                    int.from_bytes(msg[2:4], 'big'),
                    int.from_bytes(msg[4:6], 'big')
                )

            elif msg[0] == 6: # ClientCutText
                self.ClientCutText(
                    msg[6 : int.from_bytes(msg[2:6], 'big')]
                )

            else:
                self.ClientOtherMsg(msg)

        return True
    
    def ClientSetPixelFormat(self, 
                       bpp, depth, 
                       big, true, 
                       r_max, g_max, b_max, 
                       r_shift, g_shift, b_shift 
                      ):
        print('ClientSetPixelFormat',
              bpp, depth, 
              big, true, 
              r_max, g_max, b_max, 
              r_shift, g_shift, b_shift 
        )

    def ClientSetEncodings(self, encodings):
        print('ClientSetEncodings', encodings) 

    def ClientFrameBufferUpdateRequest(self, incr, x, y, w, h):
        print('ClientFrameBufferUpdateRequest', incr, x, y, w, h)

    def ClientKeyEvent(self, down, key):
        print('ClientKeyEvent', down, hex(key))        

    def ClientPointerEvent(self, buttons, x, y):
        print('ClientPointerEvent', buttons, x, y)
    
    def ClientCutText(self, text):
        print('ClientClientCutText', text)
    
    def ClientOtherMsg(self, msg):
        print('ClientOtherMsg', msg)
