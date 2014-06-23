# a controller is all the circuits and temperatures (sensors and effectors)
# equipment bytes are 1 and 2, bits 0 - 7

import circuit
import redis
import json

class controller(object):
	def __init__( self, circuitlist ):
		self.circuitlist = circuitlist
		self.watertemp = 70		# deg F
		self.spasettemp = 70		# deg F
		self.poolsettemp = 70		# deg F
		self.airtemp = 70		# deg F
		self.hash = 0			# for caching
		self.oldhash = 1
		self.r = redis.StrictRedis( host='localhost', port=6379, db=0)

	def setwatertemp( self, temp ):
		if self.watertemp != temp:
			self.watertemp = temp
			self.updatehash()

	def setspasettemp( self, temp ):
		if self.spasettemp != temp:
			self.spasettemp = temp
			self.updatehash()

	def setpoolsettemp( self, temp ):
		if self.poolsettemp != temp:
			self.poolsettemp = temp
			self.updatehash()

	def setairtemp( self, temp ):
		if self.airtemp != temp:
			self.airtemp = temp
			self.updatehash()

	def getwatertemp( self ):
		return self.watertemp

	def getspasettemp( self ):
		return self.spasettemp

	def getpoolsettemp( self ):
		return self.poolsettemp

	def getairtemp( self ):
		return self.airtemp

	def updatehash(self):
		h = 0
		for a in self.circuitlist:
			h += a.getHash()
		h += int(self.watertemp) * 1000
		h += int(self.spasettemp) * 100
		h += int(self.poolsettemp) * 50
		h += int(self.airtemp) * 10
		self.hash = h
		return h

	def gethash( self ):
		return self.hash
	
	def appendcircuit( self, c ):
		self.circuitlist.append( c )

	def setcircuit( self, equipbyte, equipbit, val ):
		# find circuit and set to val
		retval = False
		for c in self.circuitlist:
			if c.match( equipbyte, equipbit ):
				#if val == 1:
				#	print "setting %s to %s" % (c.getname, val)
				c.setState( val )
				self.updatehash()
				retval = True
				break
		return retval

	def getcircuitlist( self ):
		return self.circuitlist

	def getcircuitnumstate( self, circuitnum ):
		for c in self.circuitlist:
			if c.getNumber() == circuitnum:
				return c.getState()
		return -1	# not found

	# save to redis as a hash with values
	def save( self ):
		# only save if we have to
		if self.oldhash == self.hash:
			return False
		else:
			d = {}
			for c in self.circuitlist:
				d[c.getNumber()] = json.dumps(c.todict())
			d["airtemp"] = self.airtemp
			d["watertemp"] = self.watertemp
			d["spasettemp"] = self.spasettemp
			d["poolsettemp"] = self.poolsettemp
			d["hash"] = self.hash
			# pool is the redis hash key, so you can do a 
			# redis-cli hgetall pool
			# to see all the data stored in redis
			self.r.hmset( "pool", d )
			self.oldhash = self.hash

	def load( self ):
		# get dictionary from redis
		d = self.r.hgetall( "pool" )
		# and sort it all out
		self.circuitlist = []		# empty
		for k in d.keys():
			if k == "hash":
				self.hash = d[k]
			elif k == "airtemp":
				self.airtemp = d[k]
			elif k == "watertemp":
				self.watertemp = d[k]
			elif k == "spasettemp":
				self.spasettemp = d[k]
			elif k == "poolsettemp":
				self.poolsettemp = d[k]
			elif int(k) > 0 and int(k) < 16:		# circuit
				# decode json sting
				cdict = json.loads(d[k])				
				self.circuitlist.append( circuit.circuit(k,
								cdict["name"],
								cdict["byte"],
								cdict["bit"],
								cdict["value"] ))
			else:
				print "bad key %s found in load" % k
		self.oldhash = self.hash

		
