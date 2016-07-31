try:
    from uos import stat
except:
    from os import stat

import http


def MyRequestHandler(request, conn):

    if request.method == "GET":
        uri = request.uri.path \
                + ("/" if request.uri.path else "") \
                + (request.uri.file if request.uri.file else "index.html")

        try:
            stat(uri)
        except:
            conn.send( b"HTTP/1.1 404 Not Found\r\n\r\n" )
            return

        conn.send( b"HTTP/1.1 200 OK\r\n\r\n" )

        _buf = bytearray(128)
        buf = memoryview(_buf)
        with open(uri, "rb") as file:
            while True:
                count = file.readinto(buf)
                if count:
                    conn.send(buf[:count])
                else:
                    break 

        conn.send( b"\r\n" )
    
    else:
        # catch all request types
        conn.send(b"HTTP/1.1 403 Not Implemented\r\n\r\n")
    

srv = http.HttpServer(callback=MyRequestHandler)
srv.serve()