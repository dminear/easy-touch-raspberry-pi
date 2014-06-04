#! /usr/bin/python

import urllib
import time
import serial
import string
import sys
import os

def updateVera(device,variable,value):
        url="http://192.168.1.28:3480/data_request?id=variableset&DeviceNum=%d&serviceId=urn:upnp-org:serviceId:VContainer1&Variable=Variable%d&Value=%s" % (device,variable,value)
        #print "Updating Vera: ",url
        f = urllib.urlopen(url);



output = " "
ser = serial.Serial('/dev/ttyAMA0', baudrate=9600, timeout=3)

data=[]
for x in range(128):
	output = ser.read()
	d=ord(output)
	data.append(d)
	print x,"\t",d,"\t",hex(d),"\t","{0:08b}".format(d)


## find start of packet
start=[255,255,255,255,0,255,165,39]

startBit=0;
for x in range(118):
	if data[x]==start[0] and startBit==0:
		if data[x+1]==start[1]:
			if data[x+2]==start[2]:
				if data[x+3]==start[3]:
					if data[x+4]==start[4]:
						if data[x+5]==start[5]:
							if data[x+6]==start[6]:
								if data[x+7]==start[7]:
									startBit=x+6
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

