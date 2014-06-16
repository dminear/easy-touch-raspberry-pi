
'''

Equipment byte 1: this is byte 11 (zero based) from status packet starting with 'ff 00 ff a5'

bit 7 - pool lights on
bit 6 - slide valve activated 
bit 5 - pool pump
bit 4 - waterfall motor on 
bit 3 - spillway motor on
bit 2 - jets 2 on
bit 1 - jets 1 on
bit 0 - 

Equipment byte 2: this is byte 12 (zero based) from status packet starting with 'ff 00 ff a5'

bit 7 - 
bit 6 - 
bit 5 - 
bit 4 -
bit 3 - 
bit 2 - 
bit 1 - 
bit 0 - spa light

'''

class circuit (object):
	def __init__(self, number, name, equipmentbyte, equipmentbit):
		self.number = number
		self.name = name
		self.byte = equipmentbyte
		self.bit = equipmentbit
		self.value = 0

	def getName( self ):
		return self.name

	def getState( self ):
		return self.value

	def setState( self, val ):
		self.value = val
		return self

	def match( self, byte, bit):
		if self.byte == byte and self.bit==bit:
			return True
		else:
			return False

	def getHash( self ):
		return (int(self.number) * 1000 +
			int(self.byte) * 100 +
			int(self.bit) * 10 +
			int(self.value))



