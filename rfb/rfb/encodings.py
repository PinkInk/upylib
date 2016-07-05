try:
    from ustruct import pack
except:
    from struct import pack

RAWRECT = 0
COPYRECT = 1
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
    # else: colourmap not implemented


class BasicRectangle:

    encoding = None

    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self._w = w
        self._h = h
    
    @property
    def w(self): 
        return self._w

    @property
    def h(self): 
        return self._h

    # return bytes or
    #   None = delete from rectangles
    #   False = no update required
    def to_bytes(self):
        return pack('>4HL',
                    self.x, self.y,
                    self.w, self.h,
                    self.encoding
               )


class CopyRect(BasicRectangle):

    encoding = COPYRECT

    def __init__(self,
                 x, y,
                 w, h,
                 src_x, src_y
                ):
        super().__init__(x, y, w, h)
        self.src_x = src_x
        self.src_y = src_y

    def to_bytes(self):
        return super().to_bytes() \
               + pack('>2H', self.src_x, self.src_y) 


class ColourRectangle(BasicRectangle):

    def __init__(self, 
                 x, y, 
                 w, h, 
                 bpp, depth, 
                 big, true,
                 masks, shifts 
                ):
        super().__init__(x, y, w, h)
        self._bpp = bpp
        self._depth = depth
        self._big = big
        self._true = true
        self._masks = masks
        self._shifts = shifts

    @property 
    def bpp(self): 
        return self._bpp

    @property
    def depth(self): 
        return self._depth

    @property
    def big(self):
        return self._big    

    @property
    def true(self): 
        return self._true
    
    @property
    def masks(self):
        return self._masks
    
    @property
    def shifts(self):
        return self._shifts


class RawRect(ColourRectangle):

    encoding = RAWRECT

    def __init__(self, 
                 x, y, 
                 w, h, 
                 bpp, depth, 
                 big, true,
                 masks, shifts 
                ):
        super().__init__(x, y, w, h, bpp, depth, big, true, masks, shifts)
        self.buffer = bytearray( (bpp//8)*w*h )

    def fill(self, colour):
        stop = self.w*self.h*(self.bpp//8)
        step = self.bpp//8
        for i in range(0, stop, step):
            self.buffer[i : i+step] = colour_to_pixel(
                                                colour, 
                                                self.bpp, self.depth, 
                                                self.big, self.true, 
                                                self.masks, self.shifts
                                      )

    def setpixel(self, x, y, colour):
        start = (y * self.w * (self.bpp//8)) + (x * (self.bpp//8))
        step = self.bpp//8
        self.buffer[start : start+step] = colour_to_pixel(
                                                colour, 
                                                self.bpp, self.depth, 
                                                self.big, self.true, 
                                                self.masks, self.shifts
                                          )
    
    def to_bytes(self):
        return super().to_bytes() \
               + self.buffer


class RRESubRect(ColourRectangle):

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


class RRERect(ColourRectangle):

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
