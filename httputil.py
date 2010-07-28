import BaseHTTPServer
import httplib
import util

def request(host, path, postdata = None):
	if postdata == None:
		type = "GET"
		body = ""
	else:
		type = "POST"
		body = postdata
	connection = httplib.HTTPConnection(util.host(host), util.port(host), True, 10)
	connection.request(type, path, body)
	response = connection.getresponse()
	data = response.read()
	connection.close()
	return data

def errorhandler(s):
	def h(request):
		return 501, s
		

class handler(BaseHTTPServer.BaseHTTPRequestHandler):
	def do_ALL(self):
		x = self.path.split("?", 2)
		self.args = {}
		if len(x) == 2:		
			plainpath, args = x
			args = args.split("&")
			for x2 in args:
				x3 = x2.split("=")
				if len(x3) == 2:
					k, v = x3
					self.args[k] = v
		else:
			plainpath = x[0]

		length = self.headers.get('Content-Length')
		if length != None:
			length = int(length)
			self.postdata = self.rfile.read(length)
		else:
			self.postdata = None
		
		handlers = self.server.handlers
		command = plainpath.split("/", 3)[1]
		if command == None:
			h = errorhandler("No command found in path: " + plainpath)
		else:
			h = handlers[command]
		code, data = h(self)
		self.send_response(code)
		self.send_header('Content-type', 'text/plain')
		self.end_headers()
		self.wfile.write(data)
		
	def do_GET(self):
		self.do_ALL()
		
	def do_POST(self):
		self.do_ALL()
	
	def log_request(self, code='-', size='-'):
		pass
		
def createserver(port, handlers):
	server_address = ('', port)
	httpd = BaseHTTPServer.HTTPServer(server_address, handler)
	httpd.handlers = handlers	
	return httpd

