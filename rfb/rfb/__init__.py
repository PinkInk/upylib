try:
    import usocket as socket
except:
    import socket
from rfb.session import *
from rfb.servermsgs import *
from rfb.encodings import *

try: # mpy/cpython compat in main loop
    BlockingIOError
except:
    class BlockingIOError(Exception):
        pass
    class ConnectionAbortedError(Exception):
        pass
    class ConnectionResetError(Exception):
        pass


class RfbServer():

    def __init__(self, 
                 w, h, 
                 name = b'rfb', 
                 handler = RfbSession,
                 addr = ('0.0.0.0', 5900), #mpy doesn't like b'' 
                 backlog = 3,
                ):
        self.w = w
        self.h = h
        # rfb session init fails with 0 length name
        if len(name) < 1:
            raise ValueError('name cannot be empty')
        self.name = name if type(name) is bytes else bytes(name,'utf-8')
        self.handler = handler
        self.sessions = []
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setblocking(False) # unix mpy has no .settimeout(0)?
        self.s.bind( socket.getaddrinfo(addr[0],addr[1])[0][-1] ) # req'd by mpy
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
        except (OSError, BlockingIOError): # mpy, cpython
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
                except (OSError, ConnectionAbortedError, ConnectionResetError):
                    del( self.sessions[idx] )
