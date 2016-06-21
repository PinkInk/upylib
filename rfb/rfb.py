#https://github.com/rfbproto/rfbproto/blob/master/rfbproto.rst
import socket
try:
    import struct
except:
    import ustruct as struct

s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.bind(('127.0.0.1',5902))
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
SEC_INVALID = 0x0
SEC_NONE = 0x1
SEC_VNCAUTH = 0x2
SEC_TIGHT = 0x10
SEC_VENCRYPT = 0x13

conn.send( struct.pack('!I', SEC_NONE) )

#ClientInit
#----------
d = conn.recv(1024)
if d[0] == 1:
    print('other clients can be left connected')
elif d[0] == 0:
    print('disconnect other clients')
else:
    print('invalid ClientInit from client')

#ServerInit
#----------
desk_name = b'desktop'

#framebuffer width
#framebuffer height
#pixel format:
#   bits per pixel 8,16 or 32
#   depth = used bits per pixel for e.g. 24 for r,g,b 8
#   big-endian flag >0=True
#   true-color flag >0=True - 0 == colormap required
#   red, green and blue max values
#   red, green and blue bit shift values
#   3 bytes of padding
#length of desktop name
#desktop name

#svr_init = struct.pack('! 2H 4B 3H 3B 3x I ' + str(len(desk_name)) + 's', 20, 20, 32, 24, 1, 1, 0xff, 0xff, 0xff, 0, 8, 16, len(desk_name), desk_name)

svr_init = struct.pack('!2H4B3H3B', 20, 20, 32, 24, 1, 1, 0xff, 0xff, 0xff, 0, 8, 16)

conn.send(svr_init)

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
