import rfb
try:
    from urandom import getrandbits
except:
    from random import getrandbits

class Tetris(rfb.RfbSession):

    colours = (
            (0,0,0), # 0, black 
            (255,0,0), # 1, red
            (0,255,0), # 2, green
            (0,0,255), # 3, blue
            (255,255,0), # 4, yellow
            (0,255,255), # 5, cyan
            (125, 125, 255), # 6, purple
            (255, 165, 0) # 7, orange
    )
    
    tets = (
        (
            2, 2, # width, height 
            b'\x01\x01\x01\x01', # bitmap
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
        self.fb_w = 10
        self.fb_h = 20
        self.fb = bytearray( self.fb_w*self.fb_h )
        self.fb_scale = 20
        self.tet = None
        self.spawn_tet()
    
    def spawn_tet(self):
        # self.tet = self.tets[ getrandbits(8)%len(self.tets) ]
        self.tet = self.tets[1]
        print(self.tet[0], self.tets[1][0])
        self.tet[0] = 32
        print(self.tet[0], self.tets[1][0])



svr = rfb.RfbServer(
    (10*20), (20*20),
    name = b'Tetris',
    handler = Tetris, 
)
svr.serve()