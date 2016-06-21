import socket, struct

s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('',5900))
s.listen(3)

conn, (caddr, cport) = s.accept()
print('connection from ' + caddr + '::' + str(cport))

ProtocolVersion = b'RFB 003.003\n'
conn.send(ProtocolVersion)
d = conn.recv(1024)
if d == ProtocolVersion:
    print('client accepted proposed version')

conn.send( struct.pack('!I', 1) )
print('proposed Security None(1)')

d = conn.recv(1024)
print( 'received ClientInit(' + str(d[0]) + ')' )

w,h = 800,600
svr_init = struct.pack('!2H4B3H3B', w, h, 32, 24, 1, 1, 0xff, 0xff, 0xff, 0, 8, 16) + bytes(3) + bytes(4)
conn.send(svr_init)
print('sent ServerInit:', svr_init)

#encoding = 0
#rect_count = 1
#x,y = 0,0
#msg = bytes([0x0,0]) + rect_count.to_bytes(2, 'big')
#rect = (x).to_bytes(2, 'big') \
#       + (y).to_bytes(2, 'big') \
#       + (w).to_bytes(2, 'big') \
#       + (h).to_bytes(2, 'big') \
#       + (encoding).to_bytes(4, 'big')
#conn.send(msg + rect + bytes(w*h*4))
