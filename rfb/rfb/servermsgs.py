try:
    from ustruct import pack
except:
    from struct import pack


# used only during session init
def ServerSetPixelFormat(bpp, depth, big, true, masks, shifts):
    return pack('>4B3H3B',
                 bpp, depth, big, true,
                 masks[0], masks[0], masks[0],
                 shifts[0], shifts[1], shifts[2]
           ) + bytes(3) # pad to 16 bytes


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


# # colourmap not implemented
# def ServerSetColourMapEntries(colourmap):
#     b = b''
#     for colour in colourmap:
#         b += pack('>3H', colour[0], colour[1], colour[2])
#     return v'\x01\x00' \
#            + pack('>2H', 0, len(colourmap)) \
#            + b


def ServerBell():
    return b'\x02'


def ServerCutText(text):
    if text: # '' and b'' are False
        return b'\x03\x00' \
            + len(text) \
            + bytes(text, 'utf-8')

