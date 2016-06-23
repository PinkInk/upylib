import rfb

class Tetris(rfb.RfbSession):

    def __init__(self, conn, w, h, colourmap, name):
        super().__init__(conn, w, h, colourmap, name)
        self.rectangles = []
        rect = rfb.RawRect(
                0, 0,
                self.w, self.h,
                self.bpp, self.depth, self.true,
                self.colourmap, self.rgbshift
            )
        for y in range(rect.h):
            for x in range(rect.w):
                rect.setpixel(x,y,(x,y,x))
        self.rectangles.append(rect) 


    def update(self):
        self.send( rfb.ServerFrameBufferUpdate( self.rectangles ) )
        

a=rfb.RfbServer(160, 120, name=b'tetris', handler=Tetris)
a.serve()