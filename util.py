import random

def merge(a, b):
	a.update(b)
	return a
	
	
def host(s):
	return s.split(":")[0]
	
def port(s):
	return int(s.split(":")[1])
	
def shuffle(d):
	copy = list(d.keys())
	random.shuffle(copy)
	return copy
	
