import random
import httputil
import peerutil
import httplib
import util
import socket

class entry:
	def __init__(self, key, value, time):
		self.key = key
		self.value = value
		self.time = time
	
	def __cmp__(self, other):
		if other == None:
			return -1
		v = self.time - other.time
		if v != 0: return v
		return self.value.__cmp__(other.value)
		 
	def __str__(self):
		return self.key + "=" + self.value + " (" + str(self.time) + ")"
		
data = {}

def get(request):
	key = request.args.get("key")
	if key == None:
		return 501, "No key provided"

	entry = data.get(key)
	if entry == None:
		return 204, "No value for key " + key
		
	return 200, entry.value + "\n"

def set(request):
	key = request.args.get("key")
	if key == None:
		return 501, "No key provided"
		
	t = request.args.get("time")
	if t == None:
		return 501, "No time provided"
		
	value = request.postdata
	if value == None:
		value = request.args.get("value")
	if value == None:
		return 501, "No value provided"
	
	newentry = entry(key, value, float(t))
		
	oldentry = data.get("key")
	if oldentry == None or oldentry < newentry:
		if oldentry != None:
			print(oldentry + " is older than " + newentry)
		data[key] = newentry
		return 200, "Ok\n"

peer = peerutil.getpeer("node")

try:
	server = httputil.createserver(peer.port(), 
	{
		"get" : get,
		"set" : set,
	}
	)
except socket.error:
	print("Could not bind on port: " + str(peer.port()))
else:
	print("Storage node serving on port: " + str(peer.port()))
	peer.addself()
	server.serve_forever()

