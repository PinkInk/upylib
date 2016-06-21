import uctypes

#name = b'desktop'
name = b''

#ServerInit
desc = {
    'w': uctypes.UINT16 | 0,            #framebuffer width
    'h': uctypes.UINT16 | 2,            #framebuffer height
        #PixelFormat
        'bpp': uctypes.UINT8 | 4,           #bits per pixel (sent) valid = 8,16,32
        'depth': uctypes.UINT8 | 5,         #bits per pixel (actually used)
        'big_endian': uctypes.UINT8 | 6,    #big_endian if >1
        'true_colour':  uctypes.UINT8 | 7,  #true_color if >1, else must supply colourmap
        'r_max': uctypes.UINT16 | 8,        #bitmask red value
        'g_max': uctypes.UINT16 | 10,       #bitmask green value
        'b_max': uctypes.UINT16 | 12,       #bitmast blue value
        'r_shift': uctypes.UINT8 | 14,      #bit shift for red value
        'g_shift': uctypes.UINT8 | 15,      #bit shift for green value
        'b_shift': uctypes.UINT8 | 16,      #bit shift for blue value
        '': (uctypes.ARRAY | 17, uctypes.UINT8 | 3), #3 pad bytes
    #length of desktop name, and name
    #due to encoding into struct, cannot be changed 
    'len_name': uctypes.UINT32 | 20,
    'name': (uctypes.ARRAY | 24, uctypes.UINT8 | len(name)) 
}

data = bytearray( uctypes.sizeof(desc) )

si = uctypes.struct(
    uctypes.addressof(data),
    desc,
    uctypes.BIG_ENDIAN
)

si.w = 24
si.h = 26
si.bpp = 32
si.depth = 24
si.big_endian = 1
si.true_colour = 1
si.r_max = 255
si.g_max = 255
si.b_max = 255
si.r_shift = 0
si.g_shift = 8
si.b_shift = 16
si.len_name = len(name)
for i,j in enumerate(name):
    si.name[i] = j

bytes(si)

#bitfield test
desc = {
    'f1': uctypes.BFUINT8 | 0 | 0 << uctypes.BF_POS | 2 << uctypes.BF_LEN,
    'f2': uctypes.BFUINT8 | 0 | 2 << uctypes.BF_POS | 2 << uctypes.BF_LEN,
    'f3': uctypes.BFUINT8 | 0 | 4 << uctypes.BF_POS | 1 << uctypes.BF_LEN,
    'f4': uctypes.BFUINT8 | 0 | 5 << uctypes.BF_POS | 1 << uctypes.BF_LEN,
}
data = bytearray( uctypes.sizeof(desc) )
bt = uctypes.struct(
    uctypes.addressof(data),
    desc,
    uctypes.BIG_ENDIAN
)
