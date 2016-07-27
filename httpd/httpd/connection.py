try:
    from uio import BytesIO
except:
    from io import BytesIO

try:
    from uos import stat
except:
    from os import stat

# priority list of defaults to check via os.listdir?
DEFAULT = "index.html"
VER = b"HTTP/1.1"

class HttpConnection():

    def __init__(self, conn):
        self.default = DEFAULT
        self.conn, self.addr = conn

    def recv(self, count=1024, blocking=False):
        while blocking:
            r = self.conn.recv(count)
            if r is not None:
                return r
        try:
            return self.conn.recv(count)
        except:
            pass

    def send(self, b):
        if b:
            self.conn.send(b)

    # return true if connection to be kept alive, false otherwise
    def service_requests(self):

        msg = b""

        chunk = self.recv()
        while chunk:
            msg += chunk
            chunk = self.recv()
        else:
            if chunk == b"":
                return True

        options = {}
        f = BytesIO(msg)

        request = str(f.readline().strip(), "utf-8").split(" ")

        while True:
            option = f.readline()
            if option in (b"", b"\r\n"):
                break
            else:
                opt,val = option.split(b":",1)
                opt = str(opt.strip(), "utf-8")
                val = str(val.strip(), "utf-8")
                options[ opt ] = val 
        f.close()

        print(request, options)

        if hasattr(self, request[0].upper()):
            return eval("self."+request[0].upper()+"(request, options)")
        else:
            self.send( VER + b"403 Not Implemented\r\n\r\n")
            self.conn.close()
            return False
    
    def GET(self, request, options):
        # TODO: default files in subdir
        path = self.default if request[1] == "/" else request[1][1:]
        ftype = path
        try:
            stat(path)
        except:
            self.send( VER + b" 404 Not Found\r\n\r\n" )
            self.conn.close()
            return False
        self.send( VER + b"200 OK\r\n\r\n")
        # TODO: binary files
        with open(path, "r") as file:
            for line in file:
                self.send(bytes(line,"utf-8"))
        self.send(b"\r\n")
        if options["Connection"] and options["Connection"] == "Keep-Alive": 
            return True
        else:
            self.conn.close()
            return False
