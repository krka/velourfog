import httputil
import sys
import socket
import util

if (len(sys.argv) <= 3):
	print("Usage: " + sys.argv[0] + " <connect port> <#nodes> <redundancy>")
	sys.exit(1)
port = int(sys.argv[1])
N = int(sys.argv[2])
K = int(sys.argv[3])

nodeindex = {"value" : 0}
nodes = {}
frontendnodes = {}

def notify(node, index, receivers):
	for receiver in receivers:
		httputil.request(receiver, "/addnode?host=" + node + "&index=" + str(index))

def addnode(request):
	host = request.args.get("host")
	if host == None:
		return 501, "Missing parameter: host"
		
	if nodes.get(host) == None:
		# workaround to pythons lack of lexical scoping
		index = nodeindex["value"]
		nodeindex["value"] = index + 1	

		nodes[host] = index
		notify(host, index, frontendnodes.keys())
		
	return 200, "Ok"

def addfrontend(request):
	host = request.args.get("host")
	if host == None:
		return 501, "Missing parameter: host"
		
	frontendnodes[host] = True
	nodelist = str(N) + "\n" + str(K) + "\n"
	for node, index in nodes.iteritems():
		nodelist += node + "," + str(index) + "\n"
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

