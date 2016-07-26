try:
    from uio import BytesIO
except:
    from io import BytesIO

class HttpConnection():

    def __init__(self, conn):
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

    def service_requests(self):
        msg = b''
        chunk = self.recv()
        while chunk:
            msg += chunk
            chunk = self.recv()
        f = BytesIO(msg)
        request = str(f.readline().strip(), 'utf-8')
        request_type = str(request.split(b' ')[0].upper(), 'utf-8')
        options = {}
        while True:
            option = f.readline()
            if option in (b'', b'\r\n'):
                break
            else:
                # opt,val = option.split(b':')
                opt,val = option.split(b':',1)
                opt = str(opt.strip(), 'utf-8')
                val = str(val.strip(), 'utf-8')
                options[ opt ] = val 
        f.close()
        if hasattr(self, request_type):
            # method returns true if connection to be kept open
            return eval('self.'+request_type+'(request, options)')
        # return nothing, which is false, connection dropped
    
    def GET(self, request, options):
        print(request, options)

