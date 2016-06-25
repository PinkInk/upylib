import rfb, os

class Tetris(rfb.RfbSession):

    def __init__(self, conn, w, h, colourmap, name):
        super().__init__(conn, w, h, colourmap, name)
        self.rectangles = []

        for i in range(os.urandom(1)[0]):
            x, y = tuple(list(os.urandom(2)))
            x = x if x<self.w-10 else x-10
            y = y if y<self.h-10 else y-10
            w = h = 10
            self.rectangles.append(
                rfb.RawRect(
                    x, y,
                    w, h, 
                    self.bpp, self.depth, self.true,
                    self.colourmap, self.shift
                )
            )
            self.rectangles[-1].fill(tuple(os.urandom(3)))
        self.send( rfb.ServerFrameBufferUpdate( self.rectangles ) )

    def update(self):
        for rect in self.rectangles:
            rect.fill(tuple(os.urandom(3)))
            for i in range(10):
                rect.setpixel(i,i,(0,0,0))
        self.send( rfb.ServerFrameBufferUpdate( self.rectangles ) )
        

a=rfb.RfbServer(255, 255, name=b'tetris', handler=Tetris)
a.serve()