# mpy to/from_bytes don't support big-endian representations
# u/struct & u/ctypes are cludgy, and limited for this purpose  
def bytes_to_int(b): #big-endian
    i = 0
    for b8 in b:
        i <<= 8
        i += b8
    return i

