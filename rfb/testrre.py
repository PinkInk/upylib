import rfb

class Test(rfb.RfbSession):

    def __init__(self, conn, w, h, colourmap, name):
        super().__init__(conn, w, h, colourmap, name)
    
    def update(self):
        rectangles = [
            rfb.RRERect(
                0, 0,
                50, 50,
                (255,0,0),
                self.bpp, self.depth, self.true,
                self.colourmap
            )
        ]
        rectangles[-1].subrectangles.append(
            rfb.RRESubRect(
                0, 0,
                20, 20,
                (255,255,0),
                self.bpp, self.depth, self.true,
                self.colourmap
            )
        )
        rectangles[-1].subrectangles.append(
            rfb.RRESubRect(
                20, 20,
                20, 20,
                (0,0,255),
                self.bpp, self.depth, self.true,
                self.colourmap
            )
        )
        self.send( rfb.ServerFrameBufferUpdate( rectangles ) )

svr = rfb.RfbServer(150, 150, name=b'test', handler=Test)
svr.serve()
