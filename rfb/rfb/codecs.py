# only used constants
RectEncRaw = 0
RectEncCopyRect = 1
RectEncRRE = 2
RectEncCoRRE = 4
RectEncHextile = 5

def ServerFrameBufferUpdate(self, rectangles):
    return b'\x00\x00' \
            + len(rectangles).to_bytes(2, 'big')

# colours = ((r,g,b), (r,g,b), etc.)
def ServerSetColourMapEntries(self, colours):
    # TODO: must be a less ugly method
    b = bytearray()
    for colour in colours:
        b.extend( 
            colour[0].to_bytes(2, 'big'), 
            colour[1].to_bytes(2, 'big'), 
            colour[2].to_bytes(2, 'big') 
        )
    return b'\x01\x00' \
           + b'\x00\x01' # first colour in map is 1 \
           + len(colours).to_bytes(2, 'big') \
           + b

def ServerBell(self):
    return b'\x02'

def ServerCutText(self, text):
    return b'\x03\x00' \
           + len(text) \
           + bytes(text, 'utf-8'


class Rectangle():
    pass