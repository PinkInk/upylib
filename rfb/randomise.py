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
        for i in range( 10 ):
            x, y = rand(), rand()
            x = x if x<self.w-10 else x-10
            y = y if y<self.h-10 else y-10
            w = h = 10
            self.rectangles.append(
                rfb.RawRect(
                    x, y,
                    w, h, 
                    self.bpp, self.depth, 
                    self.big, self.true,
                    self.masks, self.shifts
                )
            )

    def update(self):
        for rect in self.rectangles:
            rect.fill((
                rand(),
                rand(),
                rand(),
            ))
            for x in range(rect.w):
                for y in range(rect.h):
                    if rand()>>7:
                        rect.setpixel(
                            x, y, 
                            (rand(), rand(), rand())
                        )
        self.send( rfb.ServerFrameBufferUpdate( self.rectangles ) )


svr = rfb.RfbServer(255, 255, name=b'random', handler=Randomise)
svr.serve()