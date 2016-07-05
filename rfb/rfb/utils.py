try:
    from ustruct import pack
except:
    from struct import pack


# mpy to/from_bytes don't support big-endian representations
# u/struct & u/ctypes are cludgy, and limited for this purpose  
def bytes_to_int(b): #big-endian
    i = 0
    for b8 in b:
        i <<= 8
        i += b8
    return i

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

