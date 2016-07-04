try:
    from ustruct import pack
except:
    from struct import pack

RAWRECT = 0
COPYRECT = 1
RRERECT = 2


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
                 bpp, depth, true, 
                ):
        super().__init__(x, y, w, h)
        self._bpp = bpp
        self._depth = depth
        self._true = true

    @property 
    def bpp(self): 
        return self._bpp

    @property
    def depth(self): 
        return self._depth

    @property
    def true(self): 
        return self._true


class RawRect(ColourRectangle):

    encoding = RAWRECT

    def __init__(self, 
                 x, y, 
                 w, h, 
                 bpp, depth, true, 
                ):
        super().__init__(x, y, w, h, bpp, depth, true)
        self.buffer = bytearray( (bpp//8)*w*h )

    def fill(self, colour):
        stop = self.w*self.h*(self.bpp//8)
        step = self.bpp//8
        for i in range(0, stop, step):
            # cpython can assign slice to raw tuple
            self.buffer[i : i+(self.depth//8)] = bytes(colour)

    def setpixel(self, x, y, colour):
        start = (y * self.w * (self.bpp//8)) + (x * (self.bpp//8))
        step = self.depth//8
        # cpython can assign slice to raw tuple
        self.buffer[start : start+step] = bytes(colour)
    
    def to_bytes(self):
        return super().to_bytes() \
               + self.buffer


class RRESubRect(ColourRectangle):

    def __init__(self,
                 x, y,
                 w, h, 
                 colour,
                 bpp, depth, true,
                ):
        super().__init__(x, y, w, h, bpp, depth, true)
        self.colour = colour

    def to_bytes(self):
        # non-standard encoding, don't call super()
        return bytes(self.colour)+b'\x00' \
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
                 bpp, depth, true, 
                ):
        super().__init__(x, y, w, h, bpp, depth, true)
        self.bgcolour = bgcolour
        self.subrectangles = []

    def to_bytes(self):
        b = b''
        for rect in self.subrectangles:
            b += rect.to_bytes()
        return super().to_bytes() \
               + pack('>L',len(self.subrectangles)) \
               + bytes(self.bgcolour)+b'\x00' \
               + b
