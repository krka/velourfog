import random
import httputil
import peerutil
import httplib
import util
import time
import hashlib
import socket

def getdata(nodes, key):
	for node in nodes:
		try:
			data = httputil.request(node, "/get?key=" + key)
			return data
		except httplib.HTTPException as e:
			print(e)
	return None

def setdata(nodes, key, value, t):
	data = None
	for node in nodes:
		try:
			data = httputil.request(node, "/set?key=" + key + "&time=" + t, value)
		except httplib.HTTPException as e:
			print(e)
	return data


def get(request):
	key = request.args.get("key")
	if key == None:
		return 501, "No key provided\n"

	#preparing for partitioning
	#keyhash = hashlib.sha1(key)
	#print(keyhash.hexdigest())
	
	data = getdata(util.shuffle(peer.nodes), key)
		
	return 200, data + "\n"

def set(request):
	t = str(time.time())
	key = request.args.get("key")
	if key == None:
		return 501, "No key provided\n"
		
	value = request.postdata
	if value == None:
		value = request.args.get("value")
	if value == None:
		return 501, "No value provided\n"

	reply = setdata(peer.nodes, key, value, t)
	if reply == None:
		return 501, "internal error\n"
			
	return 200, reply + "\n"

peer = peerutil.getpeer("frontend")

try:
	server = httputil.createserver(peer.port(), 
	util.merge({
		"get" : get,
		"set" : set,
	},
	peer.gethandlers()
	)
	)
except socket.error:
	print("Could not bind on port: " + str(peer.port()))
else:
	print("Frontend node serving on port: " + str(peer.port()))
	peer.addself()
	server.serve_forever()

