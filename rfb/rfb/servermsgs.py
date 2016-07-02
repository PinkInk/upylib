# generically: return None on empty args

try:
    from ustruct import pack
except:
    from struct import pack

def ServerFrameBufferUpdate(rectangles):
    if rectangles: # empty list is False
        buffer = bytes()
        for idx,rect in enumerate( rectangles ):
            b = rect.to_bytes()
            if b is None: # done with this rectangle
                del( rectangles[idx] ) 
            elif b is False:
                pass # no update required
            else:
                buffer += b
        return b'\x00\x00' \
                + pack('>H', len(rectangles)) \
                + buffer


# colourmap as ((r,g,b), (r,g,b), (r,g,b), etc.), len<=255
def ServerSetColourMapEntries(colourmap):
    if colourmap: # () and [] are  False
        b = bytes()
        for clr in colourmap:
            for ch in clr:
                b += pack('>H', ch)
        return b'\x01\x00\x00\x00' \
            + pack('>H', len(colourmap)) \
            + b


def ServerBell():
    return b'\x02'


def ServerCutText(text):
    if text: # '' and b'' are False
        return b'\x03\x00' \
            + len(text) \
            + bytes(text, 'utf-8')
