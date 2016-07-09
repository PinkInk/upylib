import urfb

# from urandom import getrandbits
from urandom import getrandbits
def rand():
    return getrandbits(8)

import machine, gc
machine.freq(160000000)
gc.collect()

w, h, = 255, 255
rvect = 4

def update(self, parent_w, parent_h):
    if self.x+self.vector[0] <= 0 or self.x+self.w+self.vector[0] >= parent_w:
        self.vector[0] = -self.vector[0]
    if self.y+self.vector[1] <=0 or self.y+self.h+self.vector[1] >= parent_h:
        self.vector[1] = -self.vector[1]
    self.x += self.vector[0]
    self.y += self.vector[1]


class Bounce(urfb.RfbSession):

    def __init__(self, conn, w, h, name):
        super().__init__(conn, w, h, name)

        self.rectangles = [
            urfb.RRERect( # background (clear previous frame)
                0, 0,
                w, h,
                (0,0,0),
                self.bpp, self.depth, 
                self.big, self.true,
                self.masks, self.shifts
                )
        ]
        
        self.large = urfb.RRERect( # large bouncing square
                                 w//2-25, h//2-25,
                                 50, 50,
                                 (255, 255, 255),
                                 self.bpp, self.depth, 
                                 self.big, self.true,
                                 self.masks, self.shifts
                                )
        # vector must be mutable
        # esp's entropy doesn't seem too good ;o)
        self.large.vector = [rand()//50+1, rand()//50+1]
        self.large.update = update

        self.small = urfb.RRESubRect( # inner square
                                    self.large.w//2, self.large.h//2,
                                    20, 20,
                                    (0,0,0),
                                    self.bpp, self.depth, 
                                    self.big, self.true,
                                    self.masks, self.shifts
                                   )
        # vector must be mutable
        # esp's entropy doesn't seem too good ;o)
        self.small.vector = [rand()//50+1, rand()//50+1]
        self.small.update = update

        self.large.subrectangles.append( self.small )
        self.rectangles.append( self.large )

    def update(self):
        self.send( urfb.ServerFrameBufferUpdate( self.rectangles ) )
        self.small.update(self.small, self.large.w, self.large.h)
        self.large.update(self.large, w, h)


svr = urfb.RfbServer(w, h, name=b'bounce', handler=Bounce)
svr.serve()