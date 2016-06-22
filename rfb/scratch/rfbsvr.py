import socket, time

class RfbServer():

    def __init__(self, w, h, name=b'rfb', addr=('', 5900), backlog=3, sleep=1):
        self.w = w
        self.h = h
        self.addr = addr
        # rfb session init fails with 0 length name
        if len(name) < 1:
            raise ValueError('RfbServer name cannot be empty')
        self.name = name
        self.backlog = backlog
        self.sleep = sleep
        self.sessions = []
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(0)

    def serve(self, delay=1):
        print(self.addr)
        self.s.bind(self.addr)
        self.s.listen(self.backlog)

        while True:

            try:
                self.sessions.append( 
                    RfbSession(self.s.accept(),
                               self.w, 
                               self.h,
                               self.name
                    )
                )
            # except: pass
            except Exception as e: 
                print(e)

            for idx,session in enumerate( self.sessions ):
                alive = session.serve_queue()
                if not alive:
                    del( self.sessions[idx] )

            time.sleep(self.sleep)

class RfbSession():

    # session init & protocol version
    _InitHandShake = b'RFB 003.003\n'
    # Security (No Security - UINT16, value 1)
    _InitSecurity = b'\x00\x00\x00\x01'

    def __init__(self, conn, w, h, name):
        self.conn, self.addr = conn
        self.w = w
        self.h = h
        self.name = name
        self.blen = 1024
        # print('new session from ' + self.addr[0] + '::' + str(self.addr[1]))

        # HandShake
        self.conn.send(self._InitHandShake)
        if self.recv(True) != self._InitHandShake:
            raise Exception('Client did not accept protocol version proposal')

        # Security
        self.conn.send(self._InitSecurity)
        # We ignore whether client tells us to disconnect other clients or not
        # 0 = disconnect others, 1 = leave others connected
        if self.recv(True)[0] not in (0,1):
            raise Exception('Client rejected security (None)')
        print(1)

        #if init raise Exception, so that new session not added to parent.sessions

    def recv(self, blocking=False):
        while blocking:
            return self.conn.recv(self.blen)

    # def send(self, b):
    #     self.conn.send(b)

    def serve_queue(self):
        print('hello')
        return True #if connection still alive, else False


if __name__ == "__main__":
    s = RfbServer(160,120,b'desktop')
    s.serve()
