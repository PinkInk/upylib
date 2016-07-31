import http.parse as parse


class HttpConnection():

    DEFAULT = "index.html"
    VER = b"HTTP/1.1"

    def __init__(self, conn, buflen=128):
        self.conn,self.addr = conn
        self.buf = memoryview(bytearray(buflen))

    # return True if connection to be kept alive, false otherwise
    # TODO: return websocket object if websocket?
    def service_requests(self):
        
        f = self.conn.makefile(mode="rb")
        line = f.readline()

        if line:

            options = {}
            option_flag = True
            data = b""
            for chunk in f.readlines():
                if option_flag:
                    if chunk != b"\r\n":
                        opt,val = str(chunk,"utf-8").split(":",1)
                        options[ opt.strip() ] = val.strip()
                    else:
                        option_flag = False
                else:
                    data += chunk
            
            request = parse.request( line, options, data )

            if hasattr(self, request.method):
                return getattr(self, request.method)(request)
            else:
                self.send( self.VER + b" 403 Not Implemented\r\n\r\n")
                self.conn.close()
                return False
        
        else:
            return True

    def send(self, b):
        if b:
            self.conn.send(b)
