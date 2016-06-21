#https://github.com/rfbproto/rfbproto/blob/master/rfbproto.rst
import socket, uctypes
#import struct

s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('',5900))
s.listen(3)

conn, (caddr, cport) = s.accept()
print('connection from ' + caddr + '::' + str(cport))

#HandShake
#---------
ProtocolVersion = b'RFB 003.003\n'
conn.send(ProtocolVersion)

d = conn.recv(1024)
if d == ProtocolVersion:
    print('client accepted proposed version')

 
#Security
#--------
#v3.3 server decides and sends type as single U32
#v3.7+  server sends list of supported types as
#           U8 # of types
#           U8 Array of typescodes, of len '# of types'
#       client decides by sending a U8 for typecode 
#SEC_INVALID = 0x0
#SEC_VNCAUTH = 0x2
#SEC_TIGHT = 0x10
#SEC_VENCRYPT = 0x13
SEC_NONE = 0x1

#conn.send( struct.pack('!I', SEC_NONE) )
conn.send( int(SEC_NONE).to_bytes(4, 'big') )

#ClientInit
#----------
d = conn.recv(1024)
if d[0] == 1:
    print('client accepted: leave other clients connected')
elif d[0] == 0:
    print('client accepted: disconnect other clients')
else:
    print('invalid ClientInit')

#ServerInit
#----------
#svr_init = struct.pack('!2H4B3H3B', 20, 20, 32, 24, 1, 1, 0xff, 0xff, 0xff, 0, 8, 16) + bytes(3) + bytes(4)
#conn.send(svr_init)

name = b'desktop' #cannot be changed, as length used to define structure template (wobbly)

si_desc = {
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

si_data = bytearray( uctypes.sizeof(si_desc) )

si = uctypes.struct(
    uctypes.addressof(si_data),
    si_desc,
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

#conn.send( bytes(svr_init) )
conn.send( si_data )

#SetColourMapEntries
#-------------------
#follows ServerInit _if_ true_colour = 0
colours = ((0,0,0), (255,0,0), (0,255,0), (0,0,255), (255,255,255))

scme_hdr = int(1).to_bytes(1, 'big') \
           + int(0).to_bytes(1, 'big') \
           + int(1).to_bytes(2, 'big') \
           + int( len(colours) ).to_bytes(2, 'big') \

#conn.send(scme_hrd)

scme_clr_desc = {
    'r': uctypes.UINT16 | 0,
    'g': uctypes.UINT16 | 2,
    'b': uctypes.UINT16 | 4,
}

scme_clr_data = bytearray( uctypes.sizeof(scme_clr_desc) )
scme_clr = uctypes.struct(uctypes.addressof(scme_clr_data), scme_clr_desc, uctypes.BIG_ENDIAN)

for (r,g,b) in colours:
    scme_clr.r = r
    scme_clr.g = g
    scme_clr.b = b
    print(scme_clr_data)

#FrameBufferUpdate
SVR_MSG_TYPE_FRAMEBUFFERUPDATE = 0x0
rect_count = 1

#msg is padded with a zero byte
msg = bytes([SVR_MSG_TYPE_FRAMEBUFFERUPDATE,0]) \
    + rect_count.to_bytes(2, 'big')

x,y = 0,0
encoding = 0 #raw
rect = (x).to_bytes(2, 'big') \
    + (y).to_bytes(2, 'big') \
    + (w).to_bytes(2, 'big') \
    + (h).to_bytes(2, 'big') \
    + (encoding).to_bytes(4, 'big') \

pixels = bytes(w*h*4) #all zero as of now = black

conn.send(msg + rect + pixels)
