import random

def merge(a, b):
	a.update(b)
	return a
	
	
def host(s):
	return s.split(":")[0]
	
def port(s):
	return int(s.split(":")[1])
	
def numpartitions(digits):
	return 2**(4 * digits)

def getdigits(N, K):	
	digits=1
	while numpartitions(digits) < N/K:
		digits += 1
	return digits


