RAWRECT = 0
COPYRECT = 1

def ServerFrameBufferUpdate(rectangles):
    b = bytearray()
    for rect in rectangles:
        b.extend( rect.to_bytes() ) 
    return b'\x00\x00' \
            + len(rectangles).to_bytes(2, 'big') \
            + b

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

    def __init__(self, 
                 x, y, 
                 w, h, 
                 bpp, depth, true, 
                 colourmap=None, shift=None
                ):
        self.encoding = RAWRECT # raw
        self.x = x
        self.y = y
        # TODO: protect props that can't change post init?
        self.w = w
        self.h = h
        self.bpp = bpp
        self.depth = depth
        self.true = true
        self.colourmap = colourmap
        self.shift = shift
        self.buffer = bytearray( (bpp//8)*w*h )

    def fill(self, colour):
        if self.true \
                and type(colour) is tuple \
                and len(colour) is 3:
            for i in range(0, self.w*self.h*(self.bpp//8), self.bpp//8):
                self.buffer[i:i+(self.depth//8)] = colour
        elif not self.true \
                and type(colour) is int \
                and 0<=colour<len(self.colourmap):
            for i in self.buffer:
                self.buffer[i] = colour
        else:
            raise Exception('setpixel: invalid colour', colour)

    def setpixel(self, x, y, colour):
        first = (y*self.w*(self.bpp//8))+(x*(self.bpp//8))
        if self.true \
                and type(colour) is tuple \
                and len(colour)==3:
            # blurk!!!
            self.buffer[first] = colour[0]
            self.buffer[first+1] = colour[1]
            self.buffer[first+2] = colour[2]            
        elif not self.true \
                and type(colour) is int \
                and 0<=colour<len(self.colourmap):
            self.buffer[first] = colour
        else:
            raise Exception('setpixel: invalid colour', colour)
    
    def to_bytes(self):
        return self.x.to_bytes(2, 'big') \
               + self.y.to_bytes(2, 'big') \
               + self.w.to_bytes(2, 'big') \
               + self.h.to_bytes(2, 'big') \
               + self.encoding.to_bytes(4, 'big') \
               + self.buffer
