try:
    from uos import stat
except:
    from os import stat

import http


def MyRequestHandler(request, conn):

    if request.method == "GET":
        uri = request.uri.path \
                + ("/" if request.uri.path else "") \
                + (request.uri.file if request.uri.file else "simple.html")

        try:
            stat(uri)
        except:
            conn.send( b"HTTP/1.1 404 Not Found\r\n\r\n" )
            return

        conn.send( b"HTTP/1.1 200 OK\r\n\r\n" )

        with open(uri, "rb") as file:
            conn.send( file.read() )

        conn.send( b"\r\n" )
    
    else:
        # catch all request types
        conn.send(b"HTTP/1.1 403 Not Implemented\r\n\r\n")
    

srv = http.HttpServer(callback=MyRequestHandler)
srv.serve()