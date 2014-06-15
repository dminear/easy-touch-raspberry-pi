#!/usr/bin/python

import serialThread
import httpThread
import time
import sys
import circuit

# set up circuits
# I just guessed at circuit number; it is really a label tied to byte/bit
circuits = {	1 : { 'name' : 'pool light', 'byte' : 1, 'bit' : 7 },
		2 : { 'name' : 'slide', 'byte' : 1, 'bit' : 6 },
		3 : { 'name' : 'pool pump', 'byte' : 1, 'bit' : 5 },
		4 : { 'name' : 'waterfall', 'byte' : 1, 'bit' : 4 },
		5 : { 'name' : 'spillway', 'byte' : 1, 'bit' : 3 },
		6 : { 'name' : 'jets 2', 'byte' : 1, 'bit' : 2 },
		7 : { 'name' : 'jets 1', 'byte' : 1, 'bit' : 1 },
		8 : { 'name' : 'spa light', 'byte' : 2, 'bit' : 0 },
	}

circuitlist=[]
for k in circuits.keys():
	circuitlist.append( circuit.circuit( 	k,
						circuits[k]['name'],
						circuits[k]['byte'],
						circuits[k]['bit']
						))


# pass the circuits to the serial thread for decoding and stuffing
# in the redis database

serialT = serialThread.serialThread( '/dev/ttyAMA0', circuitlist, 2)
httpT = httpThread.httpThread(1,2)

serialT.start()
httpT.start()

bExit = False

while not bExit:
	try: 
		line = sys.stdin.readline()
	except:
		bExit=True
	
	if line:	
		print line

	time.sleep(1)

serialT.stop()
httpT.stop()

