import random
import httputil
import peerutil
import httplib
import util

peer = peerutil.getpeer("frontend")

peer.addself()

def getdata(nodes, key):
	for node in nodes:
		try:
			data = httputil.request(node, "/get?key=" + key)
			return data
		except httplib.HTTPException as e:
			print(e)
	return None

def setdata(nodes, key, value):
	for node in nodes:
		try:
			data = httputil.request(node, "/set?key=" + key, value)
			return data
		except httplib.HTTPException as e:
			print(e)
	return None


def get(request):
	key = request.args.get("key")
	if key == None:
		return 501, "No key provided"

	data = getdata(util.shuffle(peer.nodes), key)
		
	return 200, data + "\n"

def set(request):
	key = request.args.get("key")
	if key == None:
		return 501, "No key provided"
		
	value = request.postdata
	if value == None:
		value = request.args.get("value")
	if value == None:
		return 501, "No value provided"

	reply = setdata(util.shuffle(peer.nodes), key, value)
		
	return 200, reply + "\n"

httputil.serve(peer.port(), 
util.merge({
	"get" : get,
	"set" : set,
},
peer.gethandlers()
)
)

