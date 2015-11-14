import socket

class HTTPD:

    def __init__(self,address='', port=80, backlog=3, in_buffer_len=1024):
        self.address = address
        self.port = port
        self.backlog=backlog
        self.in_buffer_len = in_buffer_len
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind((self.address, self.port))

    def listen(self):
        self._socket.listen(self.backlog)
        while True:
            conn,addr = self._socket.accept()
            request = conn.recv(self.in_buffer_len)
            request = request.rsplit(b'\r\n')
            method = request[0].rsplit(b' ')[0]
            if   method == b'GET':     response = self.GET(request[0][1])
            elif method == b'HEAD':    response = self.HEAD(request[0][1])
            elif method == b'POST':    response = self.POST(request)
            elif method == b'PUT':     response = self.PUT(request)
            elif method == b'DELETE':  response = self.DELETE(request)
            elif method == b'TRACE':   response = self.TRACE(request)
            elif method == b'CONNECT': response = self.CONNECT(request)
            else:                      response = self.UNKNOWN(request)
            conn.send(response)
            conn.close()

    def GET(self, url):         return self.response_header(501)
    def HEAD(self,url):         return self.response_header(501)
    def POST(self, request):    return self.response_header(501)
    def PUT(self, request):     return self.response_header(501)
    def DELETE(self, request):  return self.response_header(501)
    def TRACE(self, request):   return self.response_header(501)
    def CONNECT(self, request): return self.response_header(501)

    def response_header(self, code):
        response = b'HTTP/1.1 '
        if    code==200: response += b'200 OK'
        elif  code==404: response += b'404 Not Found'
        else:            response += b'501 Not Implemented'
        return response + b'\nConnection: close\n\n'
