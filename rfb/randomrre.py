import rfb

try:
    import urandom as random
except:
    import random

class Randomise(rfb.RfbSession):

    def __init__(self, conn, w, h, colourmap, name):
        super().__init__(conn, w, h, colourmap, name)
        self.rectangles = []
    
        for i in range( random.getrandbits(8) ):
            x, y = random.getrandbits(8), random.getrandbits(8)
            w = h = random.getrandbits(5)
            x = x if x<self.w-w else x-w
            y = y if y<self.h-h else y-h
            bgcolour = (
                random.getrandbits(8),
                random.getrandbits(8),
                random.getrandbits(8)
            )
            self.rectangles.append(
                rfb.RRERect(
                    x, y,
                    w, h,
                    bgcolour,
                    self.bpp, self.depth, self.true,
                    self.colourmap                    
                )
            )

    def update(self):
        self.send( rfb.ServerFrameBufferUpdate( self.rectangles ) )
        for rect in self.rectangles:
            rect.bgcolour = (
                random.getrandbits(8),
                random.getrandbits(8),
                random.getrandbits(8),
            )


svr = rfb.RfbServer(255, 255, name=b'random', handler=Randomise)
svr.serve()