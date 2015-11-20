from uhttpsrv import uHTTPsrv

class myHTTPsrv(uHTTPsrv):
	def GET(self, addr, request):
		return 200, '<HTML><HEAD></HEAD><BODY>Hello {}</BODY></HTML>'.format(addr[0])

s=myHTTPsrv()
s.DEBUG=True
s.serve()
