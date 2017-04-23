import socket

class cdns:

    def __init__(self, ip):
        self.ip = ip
        self.udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udps.setblocking(False)
        self.udps.bind((self.ip, 53))
    
    def serve(self):
        self._serveone(self)

    async def _serveone(self):
        try:
            data, addr = self.udps.recvfrom(1024)
            if (data[2]>>3)&15 == 0: # std qry
                self.udps.sendto(
                    data[:2] + b"\x81\x80" \
                    + data[4:6]*2 \
                    + b'\x00\x00\x00\x00' \
                    + data[12:] \
                    + b'\xc0\x0c\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04' \
                    + bytes(map(int, ip.split('.'))),\
                    addr)
        except:
            pass

