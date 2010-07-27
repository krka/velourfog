import random
import httputil
import peerutil
import httplib
import util

peer = peerutil.getpeer("node")

peer.addself()

data = {}

def get(request):
	key = request.args.get("key")
	if key == None:
		return 501, "No key provided"

	value = data.get(key)
	if value == None:
		return 204, "No value for key " + key
		
	return 200, value + "\n"

def set(request):
	key = request.args.get("key")
	if key == None:
		return 501, "No key provided"
		
	value = request.postdata
	if value == None:
		value = request.args.get("value")
	if value != None:
		data[key] = value
		return 200, "Value set for key " + key + "\n"
	else:
		return 501, "No value provided"

httputil.serve(peer.port(), 
util.merge({
	"get" : get,
	"set" : set,
},
peer.gethandlers()
)
)

