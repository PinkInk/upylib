# https://tools.ietf.org/html/rfc6455

# length is a shortcut for not doing chunk encoding
# TODO: understand chunk encoding
header = """HTTP/1.x 200 OK
Connection: Keep-Alive
Content-Type: text/html; charset=UTF-8
Content-Length: {length}

"""

page = b'''
<html>
    <head>
        <title>Micropython WebSocket Test</title>
        <script language="Javascript">

            function on_load() {
                // alert("what the fuck!");
                document.getElementById("console").innerHTML += "started<BR/>";

                var conn = new WebSocket("ws://localhost");
                document.getElementById("console").innerHTML += "created socket<BR/>";

                conn.onopen = function () {
                    conn.send("ping");
                }

                conn.onerror = function (error) {
                    console.log("Websocket error: " + error);
                }

                conn.onmessage = function (msg) {
                    document.getElementById("console").innerHTML += msg+"<BR/>";
                }

            }


        </script>
    </head>
    <body onload="on_load()">
        <DIV id="console">tester<BR/></DIV>
    </body>
</html>
'''

# passed an http request (header[,body])
# returns request, {options_dict}, body
def parse_http_request(msg):
    from io import BytesIO
    f = BytesIO(msg)
    request = str(f.readline().strip(), "utf-8")
    # request_type = str(request.split(b' ')[0].upper(), 'utf-8')
    options = {}
    while True:
        option = f.readline()
        if option in (b"", b"\r\n"):
            break
        else:
            opt,val = option.split(b":",1)
            opt = str(opt.strip(), "utf-8")
            val = str(val.strip(), "utf-8")
            options[ opt ] = bytes(val, "utf-8") #leave clean values as bytes 
    body = ""
    while True:
        line = f.readline()
        if line == b"": # EOF
            break
        else:
            body += line
    f.close()
    return request, options, body
    

from .sha1 import sha1
magic = b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

addr = ('0.0.0.0', 80)
s.bind( socket.getaddrinfo(addr[0],addr[1])[0][-1] )
s.listen(3)

conn, addr = s.accept()

req = conn.recv(4096)
print(req)

conn.send(bytes(header.format(length=str(len(page))),"utf-8"))
conn.send(page)

# get the new websocket request from the page
conn, addr = s.accept()

req = conn.recv(4096)
# print(':', req)

r,o,b = parse_http_request(req)
print(r)
for i in o:
    print(i, o[i])
print(b)

import binascii

response = b"HTTP/1.x 101 Switching Protocols"

options = {}
# server should reject sessions who's Origin doesn't want to process
# Options["Origin"] # RFC doesn't specifically say this required, but probably is

# options["Host"] = o["Host"] # RFC doesn't specifically say this required, but probably is
options["Upgrade"] = b'websocket'
options["Connection"] = b'Upgrade'

# -----------------------------------------------------
# TODO: fix test understand
key = binascii.a2b_base64( o["Sec-WebSocket-Key"] ) + magic
key = sha1(key)
key = binascii.b2a_base64( key )
options["Sec-WebSocket-Accept"] = sha1( o["Sec-WebSocket-Key"]+magic )
# -----------------------------------------------------

if "Sec-Websocket-Extensions" in o:
    # client should fail connection on mismatch
    options["Sec-WebSocket-Extensions"] = o["Sec-WebSocket-Extensions"]
if "Sec-WebSocket-Protocol" in o:
    # client should fail connection on mismatch
    options["Sec-WebSocket-Protocol"] = o["Sec-WebSocket-Protocol"]

print(response)
print(options)