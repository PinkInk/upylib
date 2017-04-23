import network, socket


class CaptivePortal:

    def __init__(self, essid, auth, filen):
        self.essid = essid
        self.authmode = 1
        self.filen = filen
        self.ap = network.WLAN(network.AP_IF)
        self.ip = ''


    def start(self):
        
        # setup AP
        self.ap.active(True)
        self.ap.config(essid=self.essid, authmode=self.authmode)
        self.ip = self.ap.ifconfig()[0]
        
        # setup DNS
        self.udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udps.setblocking(False)
        self.udps.bind((self.ip, 53)) # don't bind to other interfaces
        
        # setup HTTP
        self.tcps = socket.socket()
        self.tcps.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcps.settimeout(2)
        self.tcps.bind((ip, 80))
        self.tcps.listen(1)

        while True:

            try:
                
                # DNS
                data, addr = self.udps.recvfrom(1024)
                self.udps.sendto(dnsResponse(data, self.ip), addr)
                
                # HTTP
                con = s.accept()
                

            except KeyboardInterrupt:
                break
            except:
                pass

    @staticmethod
    def dnsResponse(data, ip):
        if (data[2]>>3)&15 == 0: # std qry
            domain = ''
            ptr = 12
            len = data[ptr]
            while len != 0:
                domain += data[ptr+1:ptr+len+1].decode('utf-8') + '.'
                ptr += len+1
                len = data[ptr]
            if domain: # not an empty string
                return data[:2] + b"\x81\x80" \
                       + data[4:6]*2 \
                       + b'\x00\x00\x00\x00' \
                       + data[12:] \
                       + b'\xc0\x0c\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04' \
                       + bytes(map(int, ip.split('.')))
            return b''
        else:
            return b''


