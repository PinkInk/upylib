from uhttpsrv import uHTTPsrv

class myHTTPsrv(uHTTPsrv):
	def GET(self, addr, request):
		print(addr)
		print(addr[0])
		return 200, '<HTML><HEAD></HEAD><BODY>Hello {}</BODY></HTML>'.format(addr[0])

s=myHTTPsrv()
s.DEBUG=True
s.serve()
