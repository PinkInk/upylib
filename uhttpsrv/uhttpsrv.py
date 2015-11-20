import socket

class uHTTPsrv:

	PROTECTED = ['__init__', 'serve_once', 'serve', 'response_header', '__qualname__', '__module__', 'address', 'port', 'backlog', 'in_buffer_len', 'debug']

	def __init__(self, address='', port=80, backlog=1, in_buffer_len=1024, DEBUG=False):
		self.address = address
		self.port = port
		self.backlog = backlog
		self.in_buffer_len = in_buffer_len
		self.DEBUG = DEBUG
		self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._socket.bind((self.address, self.port))
		self._socket.listen(self.backlog)

	def serve_once(self):
		conn, addr = self._socket.accept()
		request = conn.recv(self.in_buffer_len)
		request = request.rsplit(b'\r\n')
		if self.DEBUG:
			print('REQUEST ', addr)
			for line in request: print(line)
		method = request[0].rsplit(b' ')[0].decode('utf-8')
		if method.lower() not in self.PROTECTED:
			call = getattr(self, method.upper(), False)
			if call:
				response, data = call(addr, request)
			else:
				response, data = 501, ''
		if self.DEBUG: print('RESPONSE ', response, '\n', data)
		conn.send(self.response_header(response) + data)
		conn.close()

	def serve(self):
		while True:
			self.serve_once()

	def response_header(self, code):
		return b'HTTP/1.1 ' + str(code) + b'\nConnection: close\n\n'
