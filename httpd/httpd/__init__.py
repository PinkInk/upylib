from http.connection import *

try:
    import usocket as socket
except:
    import socket

try: # mpy/cpython compat in main loop
    BlockingIOError
except:
    class BlockingIOError(Exception):
        pass


class HttpServer():

    def __init__(self,
                 handler = HttpConnection,
                 addr = ('0.0.0.0', 80),
                 backlog = 3
                ):
        self.handler = HttpConnection
        self.connections = []
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setblocking(False)
        self.s.bind( socket.getaddrinfo(addr[0], addr[1])[0][-1] )
        self.s.listen(backlog)
    
    def serve(self):
        while True:
            # microcontroller should probably sleep here
            # accept new connections
            self.accept()
            # service established connections
            self.service()
    
    def accept(self):
        try:
            self.connections.append( self.handler( self.s.accept() ) )
        except (OSError, BlockingIOError):
            pass
    
    def service(self):
        for idx,connection in enumerate( self.connections ):
            # drop connections that aren't Keep-Alive
            if not connection.service_requests():
                del( self.connections[idx] )
