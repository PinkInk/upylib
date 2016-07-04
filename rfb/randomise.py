import rfb
try:
    import urandom as random
except:
    import random

class Randomise(rfb.RfbSession):

    def __init__(self, conn, w, h, name):
        super().__init__(conn, w, h, name)
        self.rectangles = []

        # can use up to 7.6k ...
        for i in range( random.getrandbits(8) ):
            x, y = random.getrandbits(8), random.getrandbits(8)
            x = x if x<self.w-10 else x-10
            y = y if y<self.h-10 else y-10
            w = h = 10
            self.rectangles.append(
                rfb.RawRect(
                    x, y,
                    w, h, 
                    self.bpp, self.depth, self.true,
                )
            )

    def update(self):
        for rect in self.rectangles:
            rect.fill((
                random.getrandbits(8),
                random.getrandbits(8),
                random.getrandbits(8),
            ))
            for x in range(rect.w):
                for y in range(rect.h):
                    if random.getrandbits(1):
                        rect.setpixel(
                            x, y, 
                            (
                                random.getrandbits(8),
                                random.getrandbits(8),
                                random.getrandbits(8)
                            )
                        )
        self.send( rfb.ServerFrameBufferUpdate( self.rectangles ) )


svr = rfb.RfbServer(255, 255, name=b'random', handler=Randomise)
svr.serve()