import rfb
# select the correct random lib for micropython/cpython
try:
    from urandom import getrandbits
except:
    from random import getrandbits

class my_session(rfb.RfbSession):
    
    def update(self):
        x,y = getrandbits(8), getrandbits(8)
        w = h = getrandbits(5)
        # co-erce x,y to ensure rectangle doesn't overflow
        # framebuffer size (client will error out if they do)
        x = x if x<self.w-w else x-w
        y = y if y<self.h-h else y-h
        bgcolour = (getrandbits(8), getrandbits(8), getrandbits(8))
        rectangles = [
            rfb.RRERect(
                x, y, 
                w, h, 
                bgcolour,
                # refer documentation hereunder!
                self.bpp, self.depth, self.true,
                self.colourmap                    
            )
        ]
        # send a framebuffer update to the client
        self.send( rfb.ServerFrameBufferUpdate( rectangles ) )

svr = rfb.RfbServer(255, 255, handler=my_session, name=b'custom')
svr.serve()
