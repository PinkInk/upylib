# TODO: simplify with recently implemented RRERect encoding

import rfb
from os import urandom

fbw = 10
fbh = 20
fbscale = 20

class Tetris(rfb.RfbSession):
    
    tets = (
        (
            2, 2, # width, height 
            # bitmap
            b'\x01\x01\x01\x01',
            1, # colour index .. horrible; assumes colourmap ...
            False # Can rotate
        ),
        (3, 2, b'\x00\x01\x00\x01\x01\x01',         4, True),
        (3, 2, b'\x01\x01\x00\x00\x01\x01',         2, True),
        (3, 2, b'\x00\x01\x01\x01\x01\x00',         5, True),
        (4, 2, b'\x00\x00\x00\x01\x01\x01\x01\x01', 3, True),
        (4, 2, b'\x01\x00\x00\x00\x01\x01\x01\x01', 6, True),
        (4, 1, b'\x01\x01\x01\x01',                 7, True)
    )

    def __init__(self, conn, w, h, name):
        super().__init__(conn, w, h, name)
        self.fbw = fbw
        self.fbh = fbh
        self.fb = bytearray( self.fbw*self.fbh )
        self.fbscale = fbscale 

        # fill first row of framebuffer with colourmap 
        # rectangles so that we can use CopyRect subsequently
        # Use single RawRect, a 20x20 rgb buffer = 1.2kb
        rectangles = [
            rfb.RawRect(
                0, 0,
                self.fbscale, self.fbscale,
                self.bpp, self.depth, self.true,
            )          
        ]
        # !!! warning bgr not rgb !!!
        for i, colour in enumerate((
            (0,0,0), # 0, black 
            (0,0,255), # 1, red
            (0,255,0), # 2, green
            (255,0,0), # 3, blue
            (0,255,255), # 4, yellow
            (255,255,0), # 5, cyan
            (255, 125, 125), # 6, purple
            (0, 165, 255) # 7, orange
        )):
            self.fb[i] = i
            rectangles[-1].x = i*self.fbscale
            rectangles[-1].fill(colour)
            self.send( rfb.ServerFrameBufferUpdate(rectangles) )
        
        # create a tet
        # self.tet = Tet(self.fb, self.fbw, self.fbh, self.fbscale, self.send)
        self.tet_init()
        self.tet_display()

    def update(self):
        self.tet_scroll()

    def tet_scroll(self):
        # TODO: check for collisions
        # TODO: flat shape overflows buffer if it hits flat
        if self.tet_y+(self.tet_h//2) < self.fbh:
            self.tet_display(False)
            self.tet_y += 1
            self.tet_display()
        else:
            # TODO: move into background fb
            # TODO: collapse full fb rows and score points
            self.tet_init()

    def tet_init(self):            
        self.tet_w, self.tet_h, \
        self.tet_bitmap, \
        self.tet_colour, \
        self.tet_rotatable = self.tets[ urandom(1)[0]%len(self.tets) ]
        self.tet_x, self.tet_y = self.fbw//2, 1 + (self.tet_h//2)

    def tet_display(self, show=True):
        rectangles = []
        for x in range(self.tet_w):
            for y in range(self.tet_h):
                pixel = self.tet_bitmap[x+(y*self.tet_w)]
                if pixel:
                    rectangles.append(
                        self.setpixel(
                            self.tet_x-(self.tet_w//2)+x,
                            self.tet_y-(self.tet_h//2)+y,
                            self.tet_colour,
                            show
                        )
                    )
        self.send( rfb.ServerFrameBufferUpdate(rectangles) )
    
    def setpixel(self, x, y, colour, show=True):
        return rfb.CopyRect(
            x*self.fbscale, y*self.fbscale,
            self.fbscale, self.fbscale,
            colour*self.fbscale if show else 0, 0
        )


svr = rfb.RfbServer(
    fbw*fbscale, fbh*fbscale,
    name = b'Tetris',
    handler = Tetris, 
)
svr.serve()