RAWRECT = 0
COPYRECT = 1

def ServerFrameBufferUpdate(rectangles):
    b = bytearray()
    for rect in rectangles:
        b.extend( rect.to_bytes() ) 
    return b'\x00\x00' \
            + len(rectangles).to_bytes(2, 'big') \
            + b

# colourmap as ((r,g,b), (r,g,b), (r,g,b), etc.), len<=255
def ServerSetColourMapEntries(colourmap):
    b = bytearray()
    for clr in colourmap:
        for ch in clr:
            b.extend( ch.to_bytes(2, 'big') )
    return b'\x01\x00\x00\x01' \
           + len(colourmap).to_bytes(2, 'big') \
           + b

def ServerBell():
    return b'\x02'

def ServerCutText(text):
    return b'\x03\x00' \
           + len(text) \
           + bytes(text, 'utf-8')

# class CopyRect:
#     def __init__(self):
#         self.encoding = 1

class RawRect:

    encoding = RAWRECT # raw

    def __init__(self, 
                 x, y, 
                 w, h, 
                 bpp, depth, true, 
                 colourmap=None, shift=None
                ):
        self.x = x
        self.y = y
        self._w = w
        self._h = h
        self._bpp = bpp
        self._depth = depth
        self._true = true
        self._colourmap = colourmap
        self._shift = shift
        self.buffer = bytearray( (bpp//8)*w*h )
    
    @property
    def w(self): return self._w

    @property
    def h(self): return self._h

    @property 
    def bpp(self): return self._bpp

    @property
    def depth(self): return self._depth

    @property
    def true(self): return self._true

    @property
    def colourmap(self): return self._colourmap

    @property
    def shift(self): return self._shift

    def colour_is_true(self, colour):
        if self.true \
                and type(colour) is tuple \
                and len(colour) is 3:
            return True
        elif not self.true \
                and type(colour) is int \
                and 0<=colour<len(self.colourmap):
            return False
        else:
            raise Exception('invalid ' + 
                            + ('true' if self.true else 'mapped') \
                            + ' colour', colour)

    def fill(self, colour):
        if self.colour_is_true(colour):
            stop = self.w*self.h*(self.bpp//8)
            step = self.bpp//8
            for i in range(0, stop, step):
                self.buffer[i : i+(self.depth//8)] = colour
        else:
            for i in self.buffer:
                self.buffer[i] = colour

    def setpixel(self, x, y, colour):
        start = (y * self.w * (self.bpp//8)) + (x * (self.bpp//8))
        step = self.depth//8
        if self.colour_is_true(colour):
            self.buffer[start : start+step] = colour
        else:
            self.buffer[start] = colour
    
    def to_bytes(self):
        return self.x.to_bytes(2, 'big') \
               + self.y.to_bytes(2, 'big') \
               + self._w.to_bytes(2, 'big') \
               + self._h.to_bytes(2, 'big') \
               + self.encoding.to_bytes(4, 'big') \
               + self.buffer
