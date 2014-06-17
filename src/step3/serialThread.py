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

cmdLock = threading.Lock()
cmdQueue = Queue.Queue(10)

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
				c = message['data']
				print "------ CMD: %s" % (c)
				cmdLock.acquire()
				cmdQueue.put(c)
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

	def stop(self):
		self.exit = True

	def run(self):
		print "Starting serial thread"
		self.ser = serial.Serial(self.device, baudrate=9600, timeout=1)
		scanlen = 100
		inputBuffer = []
		while self.exit == False:

			#ser = serial.Serial('/dev/ttyAMA0', baudrate=9600, timeout=3)

			#ascdata=""
 			#data=[]
			
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
		# TODO do the work
		print "serialThread: cmd is %s" % (cmd)
		return True

	def processMessage( self, message ):

		if len(message) < 11:
			print "ERR: Message short:"
			for y in message:
				sys.stdout.write( "%02x " % y )
			print
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
			print "ERR: message not match length size"

		if (dest == 0x0f or dest == 0x20) or src == 0x20:
			for y in range(length+9+2):
				sys.stdout.write( "%02x " % message[y] )
			print

			print "dest %d, src %d, cmd %d, len %d, chksum %02x %02x" % (dest, src, cmd, length, chksum / 0x100, chksum % 0x100)
			print

		if dest == 0x0f and src == 0x10 and cmd == 0x02 and length == 0x1d and chksum == chkhi*256+chklo:	# status
			self.decodeStatus( message )
	


	def decodeStatus( self, data ):
			state=["OFF","ON"]
			waterTemp=23
			heaterTemp=24
			airTemp=27
			clockHours=9
			clockMinutes=10

			t=time.localtime()
			localtime = time.strftime("%H:%M",t)
			print localtime
			print "Pool Time: %02d:%02d" % (data[clockHours], data[clockMinutes])
			print "Air Temperature: ",data[airTemp]
			print "Water Temperature: ",data[waterTemp]
			#print "Heater Temperature: ",data[heaterTemp]

			# update controller values
			equip = [ "{0:08b}".format(data[11]), "{0:08b}".format(data[12]) ]
			for i in range(len(equip)):
				print "Equipment", i, ": ", equip[i]

			self.controller.setpooltemp( data[waterTemp] )
			self.controller.setairtemp( data[airTemp] )
			for byte in range(2):
				for bit in range(8):
					abit = 7 - bit
					self.controller.setcircuit(byte+1, bit, equip[byte][abit:abit+1] )
			self.controller.save()		# to database


