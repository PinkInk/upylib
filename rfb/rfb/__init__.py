import socket
from rfb.session import *

class RfbServer():

    def __init__(self, 
                 w, h, 
                 name=b'rfb', 
                 addr=('', 5900), 
                 backlog=3
                ):
        self.w = w
        self.h = h
        self.addr = addr
        # rfb session init fails with 0 length name
        if len(name) < 1:
            raise ValueError('RfbServer name cannot be empty')
        self.name = name
        self.backlog = backlog
        self.sessions = []
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(0)
        self.s.bind(self.addr)
        self.s.listen(self.backlog)


    def serve(self, delay=1):
        while True:
            #accept new connections
            self.accept()
            # handle established connections
            self.service()
    
    def accept(self):
        try:
            self.sessions.append( 
                RfbSession(self.s.accept(),
                            self.w, 
                            self.h,
                            self.name
                )
            )
        except: pass
        # except Exception as e: print(e)
    
    def service(self):
        for idx,session in enumerate( self.sessions ):
            alive = session.serve_queue()
            if not alive:
                del( self.sessions[idx] )
