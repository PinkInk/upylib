try:
    from uos import stat
except:
    from os import stat

import httpd

from httpd.websocket import *

class MyHttpConnection(httpd.HttpConnection):

    def GET(self, request):

        if is_websocket_request(request):
            
            # create websocket
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