try:
    from uos import stat
except:
    from os import stat

import httpd

class MyHttpConnection(httpd.HttpConnection):

    def GET(self, request, options, data):

        # test an option which is unlikely unless this is a websocket request first
        if "Sec-WebSocket-Key" in options \
                and "Upgrade" in options and otions["Upgrade"] == "websocket" \
                and "Connection" in options and options["Connection"] == "Upgrade" \
                and "Sec-WebSocket-Version" and options["Sec-WebSocket-Version"] == "13" \
                and "Origin" in options \
                and "Host" in options \
                and request.ver.major >= 1 and request.ver.minor >= 1:
            
            # create a websocket
            pass
        
        else:
            return self.GET_file(request)

    def GET_file(self, request):

        uri = request.uri.path + "/" + request.uri.file
        if uri == "/":
            uri = self.DEFAULT
        elif uri[0] == "/":
            uri = uri[1:]

        try:
            stat(uri)
        except:
            self.send( self.VER + b" 404 Not Found\r\n\r\n" )
            self.conn.close()
            return False

        self.send( self.VER + b"200 OK\r\n\r\n" )

        file = open(uri, "rb")

        while True:
            count = file.readinto( self.buf )
            if count:
                self.send( self.buf[:count] )
            else:
                break

        self.send( b"\r\n" )
        self.conn.close()
        return False    

srv = httpd.HttpServer(handler=MyHttpConnection)
srv.serve()