import rfb

try:
    # wipy port
    from os import urandom
    def rand():
        return urandom(1)[0] 
except:
    try:
        # unix port
        from urandom import getrandbits
        def rand():
            return getrandbits(8)
    except:
        # cpython
        from random import getrandbits
        def rand():
            return getrandbits(8)

class Randomise(rfb.RfbSession):

    def __init__(self, conn, w, h, name):
        super().__init__(conn, w, h, name)
        self.rectangles = []
    
        # constrained for wipy
        for i in range( 30 ):
            x, y = rand(), rand()
            w = h = rand()>>2
            x = x if x<self.w-w else x-w
            y = y if y<self.h-h else y-h
            bgcolour = ( rand(), rand(), rand() )
            self.rectangles.append(
                rfb.RRERect(
                    x, y,
                    w, h,
                    bgcolour,
                    self.bpp, self.depth, 
                    self.big, self.true,
                    self.masks, self.shifts
                )
            )

    def update(self):
        self.send( rfb.ServerFrameBufferUpdate( self.rectangles ) )
        for rect in self.rectangles:
            rect.bgcolour = ( rand(), rand(), rand() )


svr = rfb.RfbServer(255, 255, name=b'random', handler=Randomise)
svr.serve()