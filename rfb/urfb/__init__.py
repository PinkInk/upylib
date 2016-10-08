import usocket as socket
# import socket
from urfb.session import *
from urfb.encodings import *

class RfbServer():

    def __init__(self, 
                 w, h, 
                 name = b'rfb', 
                 handler = RfbSession,
                 addr = ('0.0.0.0', 5900),
                 backlog = 3,
                ):
        self.w = w
        self.h = h
        self.name = name
        self.handler = handler
        self.sessions = []
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setblocking(False)
        self.s.bind( socket.getaddrinfo(addr[0],addr[1])[0][-1] )
        self.s.listen(backlog)

    def serve(self):
        while True:
            #accept new connections
            self.accept()
            # handle established connections
            self.service()
    
    def accept(self):
        try:
            self.sessions.append( 
                self.handler(
                    self.s.accept(),
                    self.w, self.h,
                    self.name
                )
            )
        except OSError:
            pass

    def service(self):
        for idx,session in enumerate( self.sessions ):
            alive = session.service_msg_queue()
            if not alive:
                del( self.sessions[idx] )
            else:
                try:
                    session.update()
                # session has no update() method
                except AttributeError:
                    pass
                # session teardown
                except OSError:
                    del( self.sessions[idx] )
