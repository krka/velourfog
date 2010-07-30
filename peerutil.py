import random
import httputil
import httplib
import sys
import util
import hashlib

if (len(sys.argv) <= 2):
	print("Usage: " + sys.argv[0] + " <controller-host:port> <self-host:port>")
	sys.exit(1)

controller = sys.argv[1]
selfhost = sys.argv[2]

class peer:
	def __init__(self, type, selfhost, controller):
		self.type = type
		self.selfhost = selfhost
		self.controller = controller
		self.nodes = {}
	
	def handle_connect(self, lines):
		pass
			
	def addself(self):
		connection = httplib.HTTPConnection(util.host(self.controller), util.port(controller), True, 10)
		connection.request("GET", "/add" + self.type + "?host=" + self.selfhost)
		response = connection.getresponse()
		data = response.read()
		lines = data.split("\n")
		self.handle_connect(lines)
			
	def gethandlers(self):
		return {
			"addnode" : self.addnode_handler,
		}
		
	def port(self):
		return util.port(self.selfhost)

	def addnode_handler(self, request):
		host = request.args.get("host")
		if host == None:
			return 501, "Missing parameter: host"
		
		index = request.args.get("index")
		if index == None:
			return 501, "Missing parameter: index"
		
		index = int(index)
		self.nodes[index] = host
		return 200, "Ok\n"
		
	def partition(self, key):
		keyhash = hashlib.sha1(key).hexdigest()
		return int(keyhash[0:self.digits], 16)
	
def getpeer(type, clazz = peer):
	return clazz(type, selfhost, controller)

