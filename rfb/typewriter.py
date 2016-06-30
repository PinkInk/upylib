import rfb
# from rfb.fonts.mono4x6 import mono4x6 as font
from rfb.fonts.mono6x8 import mono6x8 as font

# TODO: either I'm having a mental spasm, or;
# for no particular reason CopyRect upwards from 
# bottom of screen doesn't work 
# (without with rfb terminal is not going to work)

class TypeWriter(rfb.RfbSession):

    def __init__(self, conn, w, h, colourmap, name):
        super().__init__(conn, w, h, colourmap, name)
        self.rectangles = []
        self.char = rfb.RawRect(
                        -font.w, # -ve font width, first char will increment   
                        self.h - font.h,
                        font.w, font.h,
                        self.bpp, self.depth, self.true,
                        self.colourmap
                    )

    def update(self):
        self.send( rfb.ServerFrameBufferUpdate( self.rectangles ) )
        # chuck any rectangles already sent to display
        self.rectangles = [] # doesn't destroy self.char

    def ClientKeyEvent(self, down, key):

        if down:

            try:
                bits = font.getbitmap_str(key)
                for idx, bit in enumerate(bits):
                    colour = bytes((255,255,255) if int(bit) else (0,0,0))
                    self.char.buffer[idx*(self.bpp//8) : idx*(self.bpp//8)+3] = colour 
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
                                self.colourmap
                        )
                    )
                    self.rectangles[-1].fill((0,0,0))
                self.char.x -= font.w
        
            if self.char.x >= self.w-font.w:
                self.CarriageReturn()
                self.char.x = 0


    def CarriageReturn(self):
        # scroll
        self.rectangles.append(
            rfb.CopyRect(
                0, 0, 
                self.w, self.h-font.h,
                0, font.h
            )
        )
        # clear
        self.rectangles.append(
            rfb.RawRect(
                0, self.h-font.h,
                self.w, font.h,
                self.bpp, self.depth, self.true, 
                self.colourmap
            )
        )


svr = rfb.RfbServer(
    80*font.w, 40*font.h, 
    name=b'typewriter', 
    handler=TypeWriter, 
)
svr.serve()