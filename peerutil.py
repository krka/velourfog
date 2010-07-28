import random
import httputil
import httplib
import sys
import util

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
				
	def addself(self):
		connection = httplib.HTTPConnection(util.host(self.controller), util.port(controller), True, 10)
		connection.request("GET", "/add" + self.type + "?host=" + self.selfhost)
		response = connection.getresponse()
		data = response.read()
		lines = data.split("\n")
		for line in lines:
			if len(line) > 0:
				self.nodes[line] = True
			
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
		
		self.nodes[host] = True
		return 200, "Ok\n"
	
def getpeer(type):
	return peer(type, selfhost, controller)

