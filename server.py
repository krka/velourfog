import BaseHTTPServer

data = {}

def run(server_class=BaseHTTPServer.HTTPServer,
        handler_class=BaseHTTPServer.BaseHTTPRequestHandler):
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

class handler(BaseHTTPServer.BaseHTTPRequestHandler):
	def do_GET(self):
		key = self.path
		value = data.get(key)
		if value != None:
			self.send_response(200)
			self.send_header('Content-type', 'text/plain')
			self.end_headers()
			self.wfile.write(value)
		else:
			self.send_response(204)
			
	def do_POST(self):
		key = self.path
		length = int(self.headers['Content-Length'])
		value = self.rfile.read(length)
		data[key] = value
		self.send_response(200)
		self.send_header('Content-type', 'text/plain')
		self.end_headers()

run(handler_class = handler)

