try:
    import usocket as socket
except:
    import socket
    # used by websocket; map readinto to recv_into for mpy/cpy compat
    socket.socket.readinto = socket.socket.recv_into

import http.parse as parse

try: # mpy/cpython compat in main loop
    BlockingIOError
except:
    class BlockingIOError(Exception):
        pass


class HttpServer():

    def __init__(self,
                 callback = None,
                 websocket_handler = None,
                 addr = ("0.0.0.0", 80),
                 backlog = 3,
                ):
        self.callback = callback
        self.websocket_handler = websocket_handler
        self.websockets = []
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setblocking(False)
        self.s.bind( socket.getaddrinfo(addr[0], addr[1])[0][-1] )
        self.s.listen(backlog)
    
    def serve(self):
        while True:
            # accept new connections
            self.accept()
            # service websockets
            self.service_websockets()
    
    def accept(self):
        try:
            conn, addr = self.s.accept()
        except (OSError, BlockingIOError):
            return

        try: # micropython 
            readline = conn.readline
        except AttributeError: # cpython
            f = conn.makefile(mode="rb")
            readline = f.readline 

        # get request
        req = readline()
        if not req:
            conn.close()
        else:
            # get options and data
            options,data = {}, b""
            option_flag = True
            line = readline()
            while line:
                if option_flag:
                    if line != b"\r\n":
                        opt,val = str(line,"utf-8").split(":",1)
                        options[ opt.strip() ] = val.strip()
                    else:
                        option_flag = False
                else:
                    data += line
                line = readline()
            
            request = parse.request( req, options, data )

            if parse.is_websocket_request(request):
                # websocket request
                if self.websocket_handler: # silently ignore if no handler
                    self.websockets.append(
                        self.websocket_handler(request, conn)
                    )
            else:
                # http request
                if self.callback:
                    self.callback(request, conn)
                else:
                    conn.send(b"HTTP/1.1 403 Not Implemented\r\n\r\n")
                conn.close()
    
    def service_websockets(self):

        # DEBUG
        if len(self.websockets)> 0: 
            print(len(self.websockets))

        for idx,websocket in enumerate( self.websockets ):
            # drop websockets whos service_frames returns False
            if not websocket.service_frames():
                del( self.websockets[idx] )
