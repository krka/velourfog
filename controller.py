import httputil
import sys
import socket

if (len(sys.argv) <= 1):
	print("Usage: " + sys.argv[0] + " <connect port>")
	sys.exit(1)
port = int(sys.argv[1])

nodes = {}
frontendnodes = {}

def notify(newhost, receivers):
	for receiver in receivers:
		httputil.request(receiver, "/addnode?host=" + newhost)

def addnode(request):
	host = request.args.get("host")
	if host == None:
		return 501, "Missing parameter: host"
		
	if nodes.get(host) == None:
		nodes[host] = True	
		notify(host, frontendnodes.keys())
		
	return 200, "Ok"

def addfrontend(request):
	host = request.args.get("host")
	if host == None:
		return 501, "Missing parameter: host"
		
	frontendnodes[host] = True
	nodelist = "\n".join(nodes.keys())
	return 200, nodelist

try:
	server = httputil.createserver(port, {
		"addnode" : addnode,
		"addfrontend" : addfrontend,
	})
except socket.error:
	print("Could not bind on port: " + str(port))
else:
	print("Controller serving on port: " + str(port))
	server.serve_forever()

