import rfb
# from rfb.fonts.mono4x6 import mono4x6 as font
from rfb.fonts.mono6x8 import mono6x8 as font

class TypeWriter(rfb.RfbSession):

    def __init__(self, conn, w, h, name):
        super().__init__(conn, w, h, name)
        self.rectangles = []
        self.char = rfb.RawRect(
                        -font.w, # -ve font width, first char will increment   
                        self.h - font.h,
                        font.w, font.h,
                        self.bpp, self.depth, self.true,
                    )

    def update(self):
        self.send( rfb.ServerFrameBufferUpdate( self.rectangles ) )
        # chuck rectangles sent to display
        self.rectangles.clear()

    def ClientKeyEvent(self, down, key):

        if down:

            try:
                bits = font.getbitmap_str(key)
                for idx, bit in enumerate(bits):
                    colour = bytes((255,255,255) if int(bit) else (0,0,0))
                    start = idx*(self.bpp//8)
                    self.char.buffer[start : start+3] = colour 
                self.rectangles.append( self.char )
                self.char.x += font.w
            except:
                pass

            if key == 65293: # <enter>
                self.CarriageReturn()
                self.char.x = -font.w
            
            if key == 65288: # <backspace>
                if self.char.x >= 0:
                    self.rectangles.append( 
                        rfb.RawRect(
                                self.char.x, self.h-font.h,
                                font.w, font.h,
                                self.bpp, self.depth, self.true,
                        )
                    )
                    self.rectangles[-1].fill((0,0,0))
                self.char.x -= font.w
        
            if self.char.x >= self.w-font.w:
                self.CarriageReturn()
                self.char.x = -font.w


    def CarriageReturn(self):
        # scroll
        self.rectangles.append(
            rfb.CopyRect(
                0, 0, 
                self.w, self.h-font.h,
                0, font.h
            )
        )
        # clear, use CopyRect to minimise mem and traffic
        self.rectangles.append(
            rfb.RawRect(
                0, self.h-font.h,
                font.w, font.h,
                self.bpp, self.depth, self.true,
            ) 
        )
        self.rectangles[-1].fill((0,0,0))
        for x in range(1, self.w//font.w):
            self.rectangles.append(
                rfb.CopyRect(
                    x*font.w, self.h-font.h,
                    font.w, font.h,
                    0, self.h-font.h
                )
            )


svr = rfb.RfbServer(
    80*font.w, 40*font.h, 
    name=b'typewriter', 
    handler=TypeWriter, 
)
svr.serve()