import httputil
import sys

if (len(sys.argv) <= 1):
	print("Usage: " + sys.argv[0] + " <connect port>")
	sys.exit(1)
port = int(sys.argv[1])

nodes = {}
frontendnodes = {}

def notify(newhost, hosts):
	for host in hosts:
		if host != newhost:
			httputil.request(host, "/addnode?host=" + newhost)

def addnode(request):
	host = request.args.get("host")
	if host == None:
		return 501, "Missing parameter: host"
		
	if nodes.get(host) == None:
		nodes[host] = True	
		notify(host, nodes.keys())
		notify(host, frontendnodes.keys())
		
		
	nodelist = "\n".join(nodes.keys())
	return 200, nodelist

def addfrontend(request):
	host = request.args.get("host")
	if host == None:
		return 501, "Missing parameter: host"
		
	frontendnodes[host] = True
	nodelist = "\n".join(nodes.keys())
	return 200, nodelist

httputil.serve(port, {
	"addnode" : addnode,
	"addfrontend" : addfrontend,
})

