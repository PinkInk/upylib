# from ustruct import pack
from struct import pack

RRERECT = 2

def colour_to_pixel(colour, bpp, depth, big, true, masks, shifts):
    if true:
        v = 0
        for channel, mask, shift in zip(colour, masks, shifts):
            v += (channel & mask)<<shift
        return pack(
                    ('>' if big else '<') + \
                    ('L' if bpp==32 else ('H' if bpp==16 else 'B')),
                    v<<(bpp-depth) if big else v
            )


class ColourRectangleBaseClass:

    encoding = None

    def __init__(self, 
                 x, y, 
                 w, h, 
                 bpp, depth, 
                 big, true,
                 masks, shifts 
                ):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.bpp = bpp
        self.depth = depth
        self.big = big
        self.true = true
        self.masks = masks
        self.shifts = shifts

    def to_bytes(self):
        return pack('>4HL',
                    self.x, self.y,
                    self.w, self.h,
                    self.encoding
               )

class RRESubRect(ColourRectangleBaseClass):

    def __init__(self,
                 x, y,
                 w, h, 
                 colour,
                 bpp, depth, big, true,
                 masks, shifts 
                ):
        super().__init__(x, y, w, h, bpp, depth, big, true, masks, shifts)
        self.colour = colour

    def to_bytes(self):
        # non-standard encoding ... don't call super()
        return colour_to_pixel(
                    self.colour, 
                    self.bpp, self.depth, 
                    self.big, self.true, 
                    self.masks, self.shifts
               ) \
               + pack('>4H', 
                      self.x, self.y,
                      self.w, self.h
               )


class RRERect(ColourRectangleBaseClass):

    encoding = RRERECT

    def __init__(self,
                 x, y,
                 w, h,
                 bgcolour,
                 bpp, depth, 
                 big, true,
                 masks, shifts 
                ):
        super().__init__(x, y, w, h, bpp, depth, big, true, masks, shifts)
        self.bgcolour = bgcolour
        self.subrectangles = []

    def to_bytes(self):
        b = b''
        for rect in self.subrectangles:
            b += rect.to_bytes()
        return super().to_bytes() \
               + pack('>L',len(self.subrectangles)) \
               + colour_to_pixel(
                    self.bgcolour, 
                    self.bpp, self.depth, 
                    self.big, self.true, 
                    self.masks, self.shifts
               ) + b
