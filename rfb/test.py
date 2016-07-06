import rfb
from rfb.fonts.mono6x8 import mono6x8 as font
try:
    from urandom import getrandbits
except:
    from random import getrandbits

class AlphabetSoup(rfb.RfbSession):

    def __init__(self, conn, w, h, name):
        super().__init__(conn, w, h, name)
        # raw rectangle to hold character bitmap
        self.rectangle = rfb.RawRect(
                                   0, 0, font.w, font.h,
                                   self.bpp, self.depth, 
                                   self.big, self.true,
                                   self.masks, self.shifts
                                  )
        self.rectangles = [ self.rectangle ]

    def update(self):

        char = getrandbits(7)
        self.rectangle.x = getrandbits(8)//font.w*font.w
        self.rectangle.y = getrandbits(8)//font.h*font.h

        # just skip this update if character isn't implemented
        # or x/y less font width/height outside buffer
        if char > 32 \
                and char < 32+font.count() \
                and self.rectangle.x+font.w < self.w \
                and self.rectangle.y+font.h < self.h:
            
            bits = font.getbitmap_str(char)

            # set font pixels in rectangle
            for idx, bit in enumerate(bits):
                self.rectangle.setpixel(
                    idx%font.w, idx//font.w,
                    (255,255,255) if bit=='1' else (0,0,0)
                )

            self.send( rfb.ServerFrameBufferUpdate( self.rectangles ) )                


svr = rfb.RfbServer(255, 255, handler=AlphabetSoup, name=b'custom')
svr.serve()