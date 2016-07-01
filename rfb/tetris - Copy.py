import rfb
from os import urandom

fbw = 10
fbh = 20
fbscale = 20

class Tetris(rfb.RfbSession):
    
    def __init__(self, conn, w, h, colourmap, name):
        super().__init__(conn, w, h, colourmap, name)
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
                self.colourmap
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
        self.tet = Tet(self.fb, self.fbw, self.fbh, self.fbscale, self.send)

    def update(self):
        self.tet.scroll()


# no longer sure that this should or needs-to be a seperate class
class Tet:

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

    def __init__(self, fb, fbw, fbh, fbscale, send):
        self.fb = fb # verify that this is a pointer to parent fb?
        self.fbw = fbw
        self.fbh = fbh
        self.fbscale = fbscale
        self.send = send # really? child sent a parents method?
        self.initshape()
        self.display()

    def scroll(self):
        # TODO: check for collisions
        # TODO: flat shape overflows buffer if it hits flat
        if self.y+(self.h//2) < self.fbh:
            self.display(False)
            self.y += 1
            self.display()
        else:
            # TODO: move into background fb
            # TODO: collapse full fb rows and score points
            self.initshape()

    def initshape(self):            
        self.w, self.h, \
        self.bitmap, \
        self.colour, \
        self.rotatable = self.tets[ urandom(1)[0]%len(self.tets) ]
        self.x, self.y = fbw//2, 1 + (self.h//2)

    def display(self, show=True):
        rectangles = []
        for x in range(self.w):
            for y in range(self.h):
                pixel = self.bitmap[x+(y*self.w)]
                if pixel:
                    rectangles.append(
                        self.setpixel(
                            self.x-(self.w//2)+x,
                            self.y-(self.h//2)+y,
                            show
                        )
                    )
        self.send( rfb.ServerFrameBufferUpdate(rectangles) )
    
    def setpixel(self, x, y, show=True):
        return rfb.CopyRect(
            x*self.fbscale, y*self.fbscale,
            self.fbscale, self.fbscale,
            self.colour*self.fbscale if show else 0, 0
        )


svr = rfb.RfbServer(
    fbw*fbscale, fbh*fbscale,
    name = b'Tetris',
    handler = Tetris, 
)
svr.serve()