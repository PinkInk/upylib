import socket, struct

s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('',5900))
s.listen(1)

conn, (caddr, cport) = s.accept()
print('connection from ' + caddr + '::' + str(cport))

s.settimeout(0)

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
name=b'desktop'
svr_init = struct.pack('!2H4B3H3B', w, h, 32, 24, 1, 1, 0xff, 0xff, 0xff, 0, 8, 16) + bytes(3) + bytes([0,0,0,len(name)]) + name
conn.send(svr_init)
print('sent ServerInit:', svr_init)

def square(x,y,w,h,rgb):
    b = bytes([0,0,0,1]) #update, 1 rect
    b += x.to_bytes(2, 'big') \
         + y.to_bytes(2, 'big') \
         + w.to_bytes(2, 'big') \
         + h.to_bytes(2, 'big') \
         + int(0).to_bytes(4, 'big')
    b += (bytes(rgb)+b'\x00')*w*h
    conn.send(b)

square(0,0,800,600,(0,0,0))

i=0
while True:
    d = conn.recv(1024)
    if not d is None:
        if d[0] == 0x5:
            i += 1 if i<255 else -254
            print(d[1])
            x = int.from_bytes(d[2:4],'big')
            y = int.from_bytes(d[4:6],'big')
            if x>5 and x<795 and y>5 and y<595:
                square(x-5, y-5,10,10,(i,i,i))






encoding = 0
rect_count = 1
msg = bytes([0x0,0]) + rect_count.to_bytes(2, 'big')
w,h = 10,10
for i in range(255):
    x = y = i
    clr = bytes([i,i,i,0])
    rect = (x).to_bytes(2, 'big') \
           + (y).to_bytes(2, 'big') \
           + (w).to_bytes(2, 'big') \
           + (h).to_bytes(2, 'big') \
           + (encoding).to_bytes(4, 'big')
    conn.send(msg + rect + (clr*w*h))