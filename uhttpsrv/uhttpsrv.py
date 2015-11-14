import socket

class uHTTPsrv:

	PROTECTED = [b'__init__', b'listen_once', b'listen', b'response_header', b'__qualname__', b'__module__', b'address', b'port', b'backlog', b'in_buffer_len', b'debug']

	def __init__(self, address='', port=80, backlog=1, in_buffer_len=1024, debug=False):
		self.address = address
		self.port = port
		self.backlog = backlog
		self.in_buffer_len = in_buffer_len
		self.debug = debug
		self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._socket.bind((self.address, self.port))
		self._socket.listen(self.backlog)

	def serve_one(self):
		conn,addr = self._socket.accept()
		request = conn.recv(self.in_buffer_len)
		request = request.rsplit(b'\r\n')
		if self.debug:
			for line in request:
				print(line)
		method = request[0].rsplit(b' ')[0].decode('utf-8')
		print(method)
		if method.lower() not in self.PROTECTED:
			if hasattr(self, method):
				response = self.response_header(200) + \
				    		eval('self.'+method+'(self,request)')
			else:
				response=self.response_header(501)
		else:
			response = self.response_header(501)
		if self.debug:
			for line in response:
				print(line)
		conn.send(response)
		conn.close()

	def serve(self):
		while True:
			self.serve_one(self)

	def response_header(self, code):
		return b'HTTP/1.1 ' + str(code) + b'\nConnection: close\n\n'
