try:
    from ustruct import pack
except:
    from struct import pack

RAWRECT = 0
COPYRECT = 1
RRERECT = 2

def colour_is_true(colour, true, colourmap):
        if true \
                and type(colour) is tuple \
                and len(colour) is 3:
            return True
        elif not true \
                and type(colour) is int \
                and 0<=colour<len(colourmap):
            return False
        else:
            raise RfbEncodingError('invalid ' + \
                                   + ('true' if true else 'mapped') \
                                   + ' colour', colour)


class Rectangle:

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


class RawRect(Rectangle):

    encoding = RAWRECT

    def __init__(self, 
                 x, y, 
                 w, h, 
                 bpp, depth, true, 
                 colourmap=None
                ):
        super().__init__(x, y, w, h)
        self._bpp = bpp
        self._depth = depth
        self._true = true
        self._colourmap = colourmap
        self.buffer = bytearray( (bpp//8)*w*h )

    @property 
    def bpp(self): 
        return self._bpp

    @property
    def depth(self): 
        return self._depth

    @property
    def true(self): 
        return self._true

    @property
    def colourmap(self): 
        return self._colourmap

    def colour_is_true(self, colour):
        return colour_is_true(colour, self.true, self.colourmap)

    def fill(self, colour):
        if self.colour_is_true(colour):
            stop = self.w*self.h*(self.bpp//8)
            step = self.bpp//8
            for i in range(0, stop, step):
                # cpython can assign slice to raw tuple
                self.buffer[i : i+(self.depth//8)] = bytes(colour)
        else:
            for i in self.buffer:
                self.buffer[i] = colour

    def setpixel(self, x, y, colour):
        start = (y * self.w * (self.bpp//8)) + (x * (self.bpp//8))
        step = self.depth//8
        if self.colour_is_true(colour):
            # cpython can assign slice to raw tuple
            self.buffer[start : start+step] = bytes(colour)
        else:
            self.buffer[start] = colour
    
    def to_bytes(self):
        return super().to_bytes() \
               + self.buffer


class CopyRect(Rectangle):

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


class RRESubRect:

    def __init__(self,
                 x, y,
                 w, h, 
                 colour,
                 bpp, depth, true,
                 colourmap = None
                ):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.colour = colour
        self._bpp = bpp
        self._depth = depth
        self._true = true
        self._colourmap = colourmap
    
    @property 
    def bpp(self): 
        return self._bpp

    @property
    def depth(self): 
        return self._depth

    @property
    def true(self): 
        return self._true

    @property
    def colourmap(self): 
        return self._colourmap

    def colour_is_true(self, colour):
        return colour_is_true(colour, self.true, self.colourmap)

    def to_bytes(self):
        return (
                 bytes(self.bgcolour)+b'\x00' \
                 if self.colour_is_true(self.bgcolour) \
                 else bytes((self.bgcolour)) \
               ) \
               + pack('>4H', 
                      self.x, self.y,
                      self.w, self.h
               )


class RRERect(Rectangle):

    encoding = RRERECT

    def __init__(self,
                 x, y,
                 w, h,
                 bgcolour,
                 bpp, depth, true, 
                 colourmap=None
                ):
        super().__init__(x, y, w, h)
        self.bgcolour = bgcolour
        self._bpp = bpp
        self._depth = depth
        self._true = true
        self._colourmap = colourmap
        self.subrectangles = []

    @property 
    def bpp(self): 
        return self._bpp

    @property
    def depth(self): 
        return self._depth

    @property
    def true(self): 
        return self._true

    @property
    def colourmap(self): 
        return self._colourmap

    def colour_is_true(self, colour):
        return colour_is_true(colour, self.true, self.colourmap)

    def to_bytes(self):
        b = b''
        for rect in self.subrectangles:
            b += rect.to_bytes()
        return super().to_bytes() \
               + pack('>L',len(self.subrectangles)) \
               + (
                   bytes(self.bgcolour)+b'\x00' \
                   if self.colour_is_true(self.bgcolour) \
                   else bytes((self.bgcolour)) \
                  ) \
               + b


class RfbEncodingError(Exception):
    pass