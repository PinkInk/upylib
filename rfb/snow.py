# TODO: debian/ubuntu default 'vncviewer' doesn't like rectangle encoding?
import rfb
try:
    from urandom import getrandbits
except:
    from random import getrandbits

class Snow(rfb.RfbSession):

    def __init__(self, conn, w, h, name):
        super().__init__(conn, w, h, name)
        self.snowflakes = []
    
    def update(self):

        # update existing flakes
        for idx, flake in enumerate(self.snowflakes):
            if flake.y + flake.h + flake.vector >= 255:
                # delete flakes that have landed on the ground
                del( self.snowflakes[idx] )
            else:
                flake.y += flake.vector

        # create new flakes
        for i in range( getrandbits(5) ):
            x = getrandbits(8)
            size = getrandbits(2)
            x = x if x<self.w-size else x-size
            vector = 3-size
            self.snowflakes.append(
                rfb.RRERect(
                    x, 0, 
                    size, size+vector,
                    (0,0,0),
                    self.bpp, self.depth, self.true,
                )
            )
            self.snowflakes[-1].vector = vector
            self.snowflakes[-1].subrectangles.append(
                rfb.RRESubRect(
                    0, vector,
                    size, size,
                    (255,255,255),
                    self.bpp, self.depth, self.true,
                )
            )
        
        self.send( rfb.ServerFrameBufferUpdate( self.snowflakes ))


svr = rfb.RfbServer(255, 255, name=b'snow', handler=Snow)
svr.serve()