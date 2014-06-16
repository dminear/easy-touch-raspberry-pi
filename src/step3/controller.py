# a controller is all the circuits and temperatures (sensors and effectors)
# equipment bytes are 1 and 2, bits 0 - 7

import circuit

class controller(object):
	def __init__( self, circuitlist ):
		self.circuitlist = circuitlist
		self.pooltemp = 70		# deg F
		self.spatemp = 70		# deg F
		self.airtemp = 70		# deg F
		self.hash = 0			# for caching

	def setpooltemp( self, temp ):
		if self.pooltemp != temp:
			self.pooltemp = temp
			self.updatehash()

	def setspatemp( self, temp ):
		if self.spatemp != temp:
			self.spatemp = temp
			self.updatehash()

	def setairtemp( self, temp ):
		if self.airtemp != temp:
			self.airtemp = temp
			self.updatehash()

	def updatehash(self):
		h = 0
		for a in self.circuitlist:
			h += a.getHash()
		h += self.pooltemp * 1000
		h += self.spatemp * 100
		h += self.airtemp * 10
		self.hash = h
		return h

	def gethash( self ):
		return self.hash

	def setcircuit( self, equipbyte, equipbit, val ):
		# find circuit and set to val
		retval = False
		for c in self.circuitlist:
			if c.match( equipbyte, equipbit ):
				c.setState( val )
				self.updatehash()
				retval = True
				break
		return retval




