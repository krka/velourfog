import random
import httputil
import peerutil
import httplib
import util
import time
import hashlib
import socket

debug = True

def getdata(nodes, key):
	if debug: print("Requesting from nodes: " + str(nodes))
	for node in nodes:
		try:
			data = httputil.request(node, "/get?key=" + key)
			return data
		except httplib.HTTPException as e:
			print(e)
	return None

def setdata(nodes, key, value, t):
	if debug: print("Setting value on nodes: " + str(nodes))
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
		
	p = peer.partition(key)
	if debug: print("Got get-request for key: " + key + " (partition: " + str(p) + ")")
	list = []
	for i in range(0, peer.K):
		list.append(peer.nodes[(i + p*peer.K) % peer.N])
		
	random.shuffle(list)
	data = getdata(list, key)
		
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

	p = peer.partition(key)
	if debug: print("Got set-request for key: " + key + " (partition: " + str(p) + ")")
	list = []
	for i in range(0, peer.K):
		list.append(peer.nodes[(i + p*peer.K) % peer.N])

	reply = setdata(list, key, value, t)
	if reply == None:
		return 501, "internal error\n"
			
	return 200, reply + "\n"

class frontend(peerutil.peer):
	def handle_connect(self, lines):
		self.N = int(lines.pop(0))
		self.K = int(lines.pop(0))

		self.digits = util.getdigits(self.N, self.K)
		self.P = util.numpartitions(self.digits)

		#if debug: print("Frontend connected: N=" + str(self.N) + ", K=" + str(self.K))
	
		for line in lines:
			if len(line) > 0:
				node, index = line.split(",")
				index = int(index)
				self.nodes[index] = node
				
		#if debug: print("Nodes: " + str(self.nodes))
	
peer = peerutil.getpeer("frontend", frontend)

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

