#!/usr/bin/python
#
# Dan Minear
# 2014-06-04
# Based on earlier code. Does not seem to be exactly what I am using. I have 
# an EasyTouch 8 channel controller.

import threading
import thread
import time
import serial
import string
import sys
import os
import Queue
import redis
import array
import logging

cmdLock = threading.Lock()
cmdQueue = Queue.Queue(10)

# this is a mapping from channel number to remote channel code that goes out
# on bus. This corresponds to the stickers on the remote
#      circuit programmed : value out on RS-485 bus
remotebuttonmap = { 
			1 : 1,
			2 : 6,
			3 : 2,
			4 : 3,
			5 : 4,
			6 : 5,
			7 : 7,
			8 : 8,
			9 : 9
		}

class cmdThread (threading.Thread):
	def __init__(self):
		self.exit = False
		self.r = redis.StrictRedis( host='localhost', port=6379, db=0)
		self.ps = self.r.pubsub()
		self.ps.subscribe(['poolcmd'])
		threading.Thread.__init__(self)
		

	def stop(self):
		self.exit = True

	def run(self):
		for message in self.ps.listen():
			if message['type'] == 'message':
				# chan = message['channel']
				command = message['data']
				cmdLock.acquire()
				cmdQueue.put(command)
				cmdLock.release()
			if self.exit == True:
				break


class serialThread (threading.Thread):
	def __init__(self, device, controller, p2):
		self.device = device
		self.controller = controller
		self.oldcontrollerhash = 0
		self.p2 = p2
		self.exit = False
		threading.Thread.__init__(self)
		logging.basicConfig( filename="serial.log", level=logging.DEBUG )

	def stop(self):
		self.exit = True

	def run(self):
		logging.info( "Starting serial thread" )
		self.ser = serial.Serial(self.device, baudrate=9600, timeout=1)
		scanlen = 100
		inputBuffer = []
		while self.exit == False:
			
			output = self.ser.read(scanlen)
			for i in output:
				inputBuffer.append( ord(i) )		# append bytes

			#data.append(ord(output))
			#ascdata += output
			#print x,"\t",d,"\t",hex(d),"\t","{0:08b}".format(d)

			if len(inputBuffer) > 50:	# start searching for packet header
  				## find start of packet
				#start=[255,255,255,255,0,255,165,39]
				start=[ 0xff, 0x00, 0xff, 0xa5]

				startByte=0;
				offsetlist = []
				for x in range(len(inputBuffer)-5):
					if inputBuffer[x] == start[0] and startByte == 0:
						if inputBuffer[x+1] == start[1]:
							if inputBuffer[x+2] == start[2]:
								#if inputBuffer[x+3] == start[3]:

								offsetlist.append(x)

								#sys.stdout.write(" : ")
								#sys.stdout.flush()
								#for y in range(x,x+20):
								#	sys.stdout.write( hex(data[y]) + " " )
								#print

								#if data[x+4]==start[4]:
								#	if data[x+5]==start[5]:
								#		if data[x+6]==start[6]:
								#			if data[x+7]==start[7]:
								#				startBit=x+6
								# now print all the matching lines

				# we now have all the sync markers, but the last one could
				# possibly be the start of the next message that is
				# coming in, so we will not process that message yet
				for s in range( len( offsetlist ) - 1 ):
					begin = offsetlist[s]
					end = offsetlist[ s + 1 ]
					# process message packet here -- starts at begin
					# to end inclusive
					message = inputBuffer[begin:end]
					self.processMessage( message )
				# shift this off the front of inputBuffer
				inputBuffer = inputBuffer[offsetlist[-1]:]

				# check for any action from http thread
				while not cmdQueue.empty():
					cmdLock.acquire()
					if not cmdQueue.empty():
						cmd = cmdQueue.get()
					cmdLock.release()
					# process command
					self.processCommand( cmd )

	def processCommand( self, cmd ):
		# command is of the form:  SET CIRCUIT 1 0
		logging.debug("Serial command is %s " % cmd)
		action = 'DUMMY'
		object = 'NONE'
		num = '0'
		val = '0'
		try:
			action, object, num, val = cmd.split()
		except ValueError:
			try:
				action, object, num = cmd.split()
			except ValueError:
				logging.debug("bad split from command")

		if action == "SET":		# continue
			if object == "CIRCUIT":		# do circuit functions
				if int(num) > 0 and int(num) < 19:	# valid circuit numbers
					# check value
					nval = int(val)
					# nval can be 0 or 1
					if nval > 1:
						nval = 1
					# look up mapping from circuit number to command circuit
					cmdchannel = remotebuttonmap[int(num)]
					
					# now form packet
					header = [ 0xFF, 0xFF, 0x00, 0xFF, 0xA5, 0x07, 0x10, 0x20 ]
					command = [ 0x86 ]
					length = [ 0x02 ]
					args = [ cmdchannel, nval ]

					output = header + command + length + args

					self.sendPacket( output )

			if object == "POOLTEMP" or object == "SPATEMP":
				if int(num) >= 35 and int(num) <= 104:
					if object == "POOLTEMP":
						poolt = int(num)
						spat = int(self.controller.getspasettemp())
					else:
						poolt = int(self.controller.getpoolsettemp())
						spat = int(num)
						
					# now form packet
					header = [ 0xFF, 0xFF, 0x00, 0xFF, 0xA5, 0x07, 0x10, 0x20 ]
					command = [ 0x88, 0x04, poolt, spat, 0x05, 0x00 ]
					output = header + command
					self.sendPacket( output )
		return True

	def sendPacket( self, output ):
		# compute checksum
		chksum = 0
		for i in range(4,len(output)):
			chksum += output[i]
		chkhi = int(chksum / 256)
		chklo = int(chksum % 256)

		output += [chkhi, chklo, 0xff, 0xff]
				
		logging.debug("-----------------output packet-------------")
		p = ''
		for i in output:
			p +=  "%02x " % i 
		logging.debug( p )
		# now make string and write it out
		packet = array.array('B', output).tostring()
		logging.debug("length of packet is %d" % len(packet))
					
		self.ser.write(packet)
		time.sleep(0.3)
		self.ser.write(packet)
		time.sleep(0.3)


	def processMessage( self, message ):

		if len(message) < 11:
			logging.debug( "ERR: Message short:" )
			h = ''
			for y in message:
				h +=  "%02x " % y 
			logging.debug( h )
			return
				
		dest = message[5]
		src = message[6]
		cmd = message[7]
		length = message[8]
		chkhi = 0
		chklo = 0	
	
		chksum = 0;
		if len(message) >= length + 9 + 2:	# good
			#compute checksum
			for x in range( 3, 8 + length + 1):	# 8 bytes + len + 1 for range func
				chksum += message[x];
			chkhi = message[length+9]
			chklo = message[length+10]
		else:
			logging.debug( "ERR: message not match length size" )

		# print out messages we are interested in
		if (dest == 0x0f or dest == 0x20) or src == 0x20:
			f = ''
			for y in range(length+9+2):
				f +=  "%02x " % message[y] 
			logging.debug( f )	
			logging.debug( " dest %02x, src %02x, cmd %02x, len %02x, chksum %02x %02x" % (dest, src, cmd, length, chksum / 0x100, chksum % 0x100) )


		if dest == 0x0f and src == 0x10 and cmd == 0x02 and length == 0x1d and chksum == chkhi*256+chklo:	# status
			self.decodeStatus( message )
		if dest == 0x0f and src == 0x10 and cmd == 0x08 and length == 0x0d and chksum == chkhi*256+chklo:	# status
			self.decodeTemperatureStatus( message )
	

	def decodeTemperatureStatus( self, data ):
			waterTemp=10
			airTemp=11
			poolsetTemp=12
			spasetTemp=13

			# update controller values
			#print "--pool Set temp is ", data[poolsetTemp]
			#print "--spa Set temp is ", data[spasetTemp]
			self.controller.setpoolsettemp( data[poolsetTemp] )
			self.controller.setspasettemp( data[spasetTemp] )
			self.controller.save()		# to database

	def decodeStatus( self, data ):
			waterTemp=23
			heaterTemp=24
			airTemp=27
			clockHours=9
			clockMinutes=10

			t=time.localtime()
			localtime = time.strftime("%H:%M",t)
			logging.debug( "  Wallclock %s, Pool Time %02d:%02d" % (localtime, data[clockHours], data[clockMinutes]))
			#print "  Air %s, Water %s" % (data[airTemp], data[waterTemp])
			#print "  Heater Temperature: ",data[heaterTemp]

			equip = [ "{0:08b}".format(data[11]), "{0:08b}".format(data[12]) ]
			for i in range(len(equip)):
				logging.debug( "  Equipment%d : %s" % (i,equip[i]))

			# update controller values
			self.controller.setwatertemp( data[waterTemp] )
			self.controller.setairtemp( data[airTemp] )
			for byte in range(2):
				for bit in range(8):
					abit = 7 - bit
					self.controller.setcircuit(byte+1, bit, equip[byte][abit:abit+1] )
			self.controller.save()		# to database


