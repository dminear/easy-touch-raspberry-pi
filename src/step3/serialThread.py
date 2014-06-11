#!/usr/bin/python
#
# Dan Minear
# 2014-06-04
# Based on earlier code. Does not seem to be exactly what I am using. I have 
# an EasyTouch 8 channel controller.

import threading
import thread
#import urllib
import time
import serial
import string
import sys
import os
import redis

#def updateVera(device,variable,value):
#        url="http://192.168.1.28:3480/data_request?id=variableset&DeviceNum=%d&serviceId=urn:upnp-org:serviceId:VContainer1&Variable=Variable%d&Value=%s" % (device,variable,value)
#        #print "Updating Vera: ",url
#        f = urllib.urlopen(url);

class serialThread (threading.Thread):
	def __init__(self, device, p1, p2):
		self.device = device
		self.p1 = p1
		self.p2 = p2
		self.exit = False
		threading.Thread.__init__(self)

	def stop(self):
		self.exit = True

	def run(self):
		print "Starting serial thread"
		self.ser = serial.Serial(self.device, baudrate=9600, timeout=1)
		scanlen = 200
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
					end = offsetlist[ s + 1 ] - 1
					# process message packet here -- starts at begin
					# to end inclusive
					for y in range( begin, end + 1 ):	# need to include end byte
						sys.stdout.write( "%02x" % inputBuffer[y] + " " )
					print
					# shift this off the front of inputBuffer
				inputBuffer = inputBuffer[offsetlist[-1]:]

				#print ascdata[begin:end]

def dummyfunction():
	print startBit
	if startBit>0:
		state=["OFF","ON"]
		packetLength=36
		waterTemp=startBit+20
		airTemp=startBit+24

		## calculate Checksum
		chksumCalc=0;	
		for x in range(startBit,startBit+packetLength-1):
			chksumCalc=chksumCalc+data[x]

		chksum=data[startBit+packetLength]+256*data[startBit+packetLength-1]
		print chksum,":",chksumCalc
		if (chksum==chksumCalc):
			t=time.localtime()
			localtime = time.strftime("%H:%M",t)
			print "Air Temperature: ",data[airTemp]
			print "Water Temperature: ",data[waterTemp]
			equip="{0:08b}".format(data[startBit+8])
			print "Equipment: \t",equip
			print "Pool Pump: \t",state[int(equip[7:8])]
			print "Cleaner: \t",state[int(equip[6:7])]
			print "Pool Light: \t",state[int(equip[5:6])]
			print "Slow Speed: \t",state[int(equip[4:5])]
			updateVera(54,1,data[waterTemp])
			updateVera(54,2,data[airTemp])
			updateVera(54,3,state[int(equip[5:6])])
			updateVera(54,4,localtime)
		else: 
			updateVera(54,1,"ERROR")
			updateVera(54,2,"ERROR")
			updateVera(54,3,"ERROR")

