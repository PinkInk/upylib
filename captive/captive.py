import socket, network, time

# AP mode
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid="freewifi", authmode=1) # no auth

CONTENT = b"""\
HTTP/1.0 200 OK

<!doctype html>
<html>
    <head>
        <title>Captive Portal</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta charset="utf8">
    </head>
    <body>
        <h1>Testing Captive Portal</h1>
    </body>
</html>
"""


class DNSQuery:

  def __init__(self, data):
    self.data = data
    self.domain = ''
    m = data[2]
    opcode = (m >> 3) & 15
    if opcode == 0: # std query
      ptr = 12
      len = data[ptr]
      while len != 0:
        self.domain += data[ ptr+1 : ptr+len+1].decode("utf-8") + '.'
        ptr += len+1
        len = data[ptr]

  def response(self, ip):
    packet = b''
    if self.domain:
      packet += self.data[:2] + b"\x81\x80"
      packet += self.data[4:6] + self.data[4:6] + b'\x00\x00\x00\x00'   # Questions and Answers Counts
      packet += self.data[12:]                                          # Original Domain Name Question
      packet += b'\xc0\x0c'                                             # Pointer to domain name
      packet += b'\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04'             # Response type, ttl and resource data length -> 4 bytes
      packet += bytes(map(int,ip.split('.')))                           # 4 bytes of IP
    return packet

def start():

    ip = ap.ifconfig()[0]

    # DNS Server
    udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udps.setblocking(False)
    udps.bind(('',53))

    # Web Server
    s = socket.socket()
    ai = socket.getaddrinfo(ip, 80)
    addr = ai[0][-1]
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)
    s.settimeout(2) # 2 second timeout and a 300ms delay ???

    counter = 0

    try:

        while True:

            # DNS
            try:
                data, addr = udps.recvfrom(1024)
                p = DNSQuery(data)
                udps.sendto(p.response(ip), addr)
            except:
                pass

            # Web
            try:
                res = s.accept()
                client_sock = res[0]
                client_addr = res[1]
                client_stream = client_sock
                req = client_stream.readline()
                while True:
                    h = client_stream.readline()
                    if h == b"" or h == b"\r\n" or h == None:
                        break
                client_stream.write(CONTENT)
                client_stream.close()
                counter += 1
            except:
                pass

            time.sleep_ms(300)

    except KeyboardInterrupt:
        pass

    udps.close()