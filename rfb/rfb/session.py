from time import sleep


class RfbSession():

    # on fail raise; to prevent invalid session at parent
    def __init__(self, conn, w, h, colourmap, name):
        self.conn, self.addr = conn
        self.w = w
        self.h = h
        self.colourmap = colourmap
        self.big = True
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
            raise Exception('peer did not accept version proposal')

        # Security
        self.send( self.security.to_bytes(4, 'big') )
        if self.recv(True)[0] not in (0,1):
            raise Exception('peer rejected security (None)')

        # ServerInit
        self.send(
            w.to_bytes(2, 'big') + h.to_bytes(2, 'big') \
            + bytes([ self.bpp ]) \
            + bytes([ self.depth ]) \
            + bytes([ self.big ]) \
            + bytes([ self.true ]) \
            + (2**(self.depth//3)-1 if self.true else 0).to_bytes(2, 'big') * 3 \
            + bytes( self.shift ) \
            + bytes(3) \
            + len(name).to_bytes(4, 'big') + name
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
        # print(b) # DEBUG
        self.conn.send(b)

    # over-ride to send remote framebuffer updates
    def update(self):
        pass

    def dispatch_msgs(self):
        msg = self.recv()

        if msg == b'': #closed by peer
            return False

        elif msg is not None:

            # TODO: handle multiple msgs in queue

            # ClientSetPixelFormat(self, bpp, depth, big, true, masks, shifts)
            if msg[0] == 1 and hasattr(self, 'ClientSetPixelFormat'): 
                self.ClientSetPixelFormat(
                    msg[2],
                    msg[3],
                    msg[4] == 1,
                    msg[5] == 1,
                    (
                        int.from_bytes(msg[6:8], 'big'),
                        int.from_bytes(msg[8:10], 'big'),
                        int.from_bytes(msg[10:12], 'big')
                    ),
                    (
                        msg[12],
                        msg[13],
                        msg[14]
                    )
                )

            # ClientSetEncodings(self, encodings)
            elif msg[0] == 2:
                encodings = \
                    [int.from_bytes(msg[i:i+4],'big') for i in range(4,len(msg),4)]
                self.encodings = encodings
                if hasattr(self, 'ClientSetEncodings'):
                    self.ClientSetEncodings(encodings)

            # ClientFrameBufferUpdateRequest(self, incr, x, y, w, h)
            elif msg[0] == 3 and hasattr(self, 'ClientFrameBufferUpdateRequest'): 
                self.ClientFrameBufferUpdateRequest(
                    msg[1] == 1,
                    int.from_bytes(msg[2:4], 'big'),
                    int.from_bytes(msg[4:6], 'big'),
                    int.from_bytes(msg[6:8], 'big'),
                    int.from_bytes(msg[8:10], 'big'),
                )

            # ClientKeyEvent(self, down, key)
            elif msg[0] == 4 and hasattr(self, 'ClientKeyEvent'):
                self.ClientKeyEvent(
                    msg[1] == 1,
                    int.from_bytes(msg[4:8], 'big')
                )

            # ClientPointerEvent(self, buttons, x, y)
            elif msg[0] == 5 and hasattr(self, 'ClientPointerEvent'): 
                self.ClientPointerEvent(
                    msg[1],
                    int.from_bytes(msg[2:4], 'big'),
                    int.from_bytes(msg[4:6], 'big')
                )

            # ClientCutText(self, text)
            elif msg[0] == 6 and hasattr(self, 'ClientCutText'):
                self.ClientCutText(
                    msg[6 : int.from_bytes(msg[2:6], 'big')]
                )

            elif msg[0] > 6 and hasattr(self, 'ClientOtherMsg'):
                self.ClientOtherMsg(msg)

        return True
    