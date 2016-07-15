import rfb

# from rfb.fonts.mono4x6 import mono4x6 as font
from rfb.fonts.mono6x8 import mono6x8 as font


class TypeWriter(rfb.RfbSession):

    def __init__(self, conn, w, h, name):
        super().__init__(conn, w, h, name)
        self.rectangles = []
        self.char = rfb.RawRect(
                         # -ve font width, first char will increment
                        -font.w, self.h-font.h,
                        font.w, font.h,
                        self.bpp, self.depth, 
                        self.big, self.true,
                        self.masks, self.shifts
                    )
        # pre-initialise rectangles required by main loop saves mem
        self.scroll = rfb.CopyRect(
                        0, 0, 
                        self.w, self.h-font.h,
                        0, font.h
                      )
        self.clear = rfb.RRERect(
                        0, self.h-font.h,
                        self.w, font.h,
                        (0,0,0),
                        self.bpp, self.depth, 
                        self.big, self.true,
                        self.masks, self.shifts
                     )
        self.backspace = rfb.RawRect(
                            0, self.h-font.h,
                            font.w, font.h,
                            self.bpp, self.depth, 
                            self.big, self.true,
                            self.masks, self.shifts
                         )


    def update(self):
        self.send( rfb.ServerFrameBufferUpdate( self.rectangles ) )
        # chuck rectangles already sent
        self.rectangles.clear()

    def ClientKeyEvent(self, down, key):

        if down:

            try:
                bits = font.getbitmap_str(key)
                for idx, bit in enumerate(bits):
                    self.char.setpixel(
                        idx%font.w, idx//font.w,
                        (255,255,255) if int(bit) else (0,0,0)
                    )
                self.rectangles.append( self.char )
                self.char.x += font.w
            except:
                pass

            if key == 65293: # <enter>
                self.CarriageReturn()
                self.char.x = -font.w
            
            if key == 65288: # <backspace>
                if self.char.x >= 0:
                    self.backspace.x = self.char.x 
                    self.rectangles.append( self.backspace )
                self.char.x -= font.w
        
            # wrap line at width
            if self.char.x >= self.w-font.w:
                self.CarriageReturn()
                self.char.x = -font.w

    def CarriageReturn(self):
        self.rectangles.append( self.scroll )
        self.rectangles.append( self.clear )


svr = rfb.RfbServer(
    80*font.w, 40*font.h, 
    name=b'typewriter', 
    handler=TypeWriter, 
)
svr.serve()
