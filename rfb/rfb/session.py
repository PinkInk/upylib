import time

# recv buffer len
# TODO: consider initable class property or
# 'loop until buffer empty' recv method, which would
# mitigate;
# - vnc generating single message len()>_BLEN 
# - msgs queuing in socket buffer sum(len())>_BLEN
_BLEN = 1024

class RfbSession():

    # session init & protocol version
    _InitHandShake = b'RFB 003.003\n'
    # Security (No Security - UINT16, value 1)
    _InitSecurity = b'\x00\x00\x00\x01'

    # if init fails; raise Exception
    # so that new session not added to parent.sessions
    def __init__(self, conn, w, h, name):
        self.conn, self.addr = conn
        self.w = w
        self.h = h
        self.name = name

        # HandShake
        self.conn.send(self._InitHandShake)
        if self.recv(True) != self._InitHandShake:
            raise Exception('Client did not accept version proposal')

        # Security
        self.conn.send(self._InitSecurity)
        # Note: ignores whether new client instructs;
        #   0 = disconnect others
        #   1 = leave others connected
        if self.recv(True)[0] not in (0,1):
            raise Exception('Client rejected security (None)')

        # ServerInit
        # TODO: determine whether int.to_bytes, ustruct 
        # or uctypes is most efficient / generally useful
        # TODO: implement variable bitdepth and colourmap
        self.conn.send(
            w.to_bytes(2, 'big') \
            + h.to_bytes(2, 'big') \
            #PixelMap
            + int(32).to_bytes(1, 'big') # bpp \
            + int(24).to_bytes(1, 'big') # depth \
            + int(1).to_bytes(1, 'big') # big-endian \
            + int(1).to_bytes(1, 'big') # true-colour \
            # + 0xff.to_bytes(2, 'big') works in cpython not upy
            + int(255).to_bytes(2, 'big') # red-max \
            + int(255).to_bytes(2, 'big') # green-max \
            + int(255).to_bytes(2, 'big') # blue-max \
            + int(0).to_bytes(1, 'big') # red-shift \
            + int(8).to_bytes(1, 'big') # green-shift \
            + int(16).to_bytes(1, 'big') # blue-shift \
            + bytes(3) # padding \
            + len(self.name).to_bytes(4, 'big') # name length \
            + self.name
        )
        #TODO: send colourmap (if not true-colour)

    def recv(self, blocking=False):
        time.sleep(0.1) # ??? init fails without delay ???
        while blocking:
            r = self.conn.recv(_BLEN)
            if r is not None:
                return r
        try:
            return self.conn.recv(_BLEN)
        except:
            pass

    def serve_queue(self):
        msg = self.recv()
        if msg == b'': #closed by remote peer
            return False
        elif msg is not None:
            # TODO: handle multiple msgs in buffer 
            if msg[0] == 1:
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
            elif msg[0] == 2:
                encodings = []
                for i in range( int.from_bytes(msg[2:4], 'big') ):
                    encodings.append(
                        # ??? this bugs-out micropython allocating
                        # unreasonable amounts of memory ??? 
                        int.from_bytes(msg[4+(i*4) : 8+(i*4)], 'big') 
                    )
                self.ClientSetEncodings(encodings)
            elif msg[0] == 3:
                self.ClientFrameBufferUpdateRequest(
                    msg[1] == 1,
                    int.from_bytes(msg[2:4], 'big'),
                    int.from_bytes(msg[4:6], 'big'),
                    int.from_bytes(msg[6:8], 'big'),
                    int.from_bytes(msg[8:10], 'big'),
                )
            elif msg[0] == 4:
                self.ClientKeyEvent(
                    msg[1] == 1,
                    int.from_bytes(msg[4:8], 'big')
                )
            elif msg[0] == 5:
                self.ClientPointerEvent(
                    msg[1],
                    int.from_bytes(msg[2:4], 'big'),
                    int.from_bytes(msg[4:6], 'big')
                )
            elif msg[0] == 6:
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
        print('SetPixelFormat',
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
    
    # TODO: server msgs don't need to be class methods
    # break out into seperate file as functions

    def ServerFrameBufferUpdate(self, rectangles):
        return b'\x00\x00' \
               + len(rectangles).to_bytes(2, 'big')
    
    def ServerSetColourMapEntries(self):
        return b'\x01\x00'
    
    def ServerBell(self):
        return b'\x02'
    
    def ServerCutText(self):
        return b'\x03\x00'


class Rectangle():
    pass