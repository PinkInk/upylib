import rfb
from rfb.fonts.mono4x6 import font


class TypeWriter(rfb.RfbSession):

    def __init__(self, conn, w, h, colourmap, name):
        print(conn, w, h, name)
        super().__init__(conn, w, h, colourmap, name)
        self.rectangles = []
        self.cursor = 0

    def update(self):
        self.send( rfb.ServerFrameBufferUpdate( self.rectangles ) )
        # once we've drawn rectangles, throw them
        self.rectangles = []

    def ClientKeyEvent(self, down, key):
        if down and 32 <= key <= len(font[2])//(font[0]*font[1]//8):
            self.rectangles.append(
                rfb.RawRect(
                    self.cursor * font[0], self.h - font[1],
                    font[0], font[1],
                    self.bpp, self.depth, self.true,
                    self.colourmap, self.shift
                )
            )
            # ----------------------------------------
            char = font[2][(key-32)*3 : (key-32)*3+1]
            # map bits to bytes optimally???
            # ----------------------------------------
            self.rectangles[-1].buffer = 
            self.cursor += 1


svr = rfb.RfbServer(
    255, 255, 
    name=b'typewriter', 
    handler=TypeWriter, 
    # colourmap=((0,0,0),(255,255,255))
)
svr.serve()