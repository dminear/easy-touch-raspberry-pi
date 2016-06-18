#!/usr/bin/python

import serialThread
import httpThread
import time
import sys
import circuit
import controller
import logging
import signal
import redis

# set up circuits
# I just guessed at circuit number; it is really a label tied to byte/bit
# byte 1 is equipment byte 1 in status message,
# byte 2 is equipment byte 2 in status message
circuits = {	
		1 : { 'name' : 'spa', 'byte' : 1, 'bit' : 0 },
		2 : { 'name' : 'pool pump', 'byte' : 1, 'bit' : 5 },
		3 : { 'name' : 'jets 1', 'byte' : 1, 'bit' : 1 },
		4 : { 'name' : 'jets 2', 'byte' : 1, 'bit' : 2 },
		5 : { 'name' : 'spillway', 'byte' : 1, 'bit' : 3 },
		6 : { 'name' : 'waterfall', 'byte' : 1, 'bit' : 4 },
		7 : { 'name' : 'slide', 'byte' : 1, 'bit' : 6 },
		8 : { 'name' : 'pool light', 'byte' : 1, 'bit' : 7 },
		9 : { 'name' : 'spa light', 'byte' : 2, 'bit' : 0 },
	}

circuitlist=[]
for k in circuits.keys():
	circuitlist.append( circuit.circuit( 	k,
						circuits[k]['name'],
						circuits[k]['byte'],
						circuits[k]['bit'],
						0
						))

bExit = False

def sigint_handler(signum, frame):
	global bExit
	# clean up and stop threads
	print "CTRL-C pressed, cleaning up"
	bExit = True

# switch to DEBUG for packet level byte data (but then that writes to the SD
# card so do not keep it there in normal operation

#logging.basicConfig( filename='debug.log', level=logging.DEBUG )
logging.basicConfig( filename='debug.log', level=logging.INFO )

# pass the circuits to the serial thread for decoding and stuffing
# in the redis database
controller = controller.controller( circuitlist )
#controller.save()
serialT = serialThread.serialThread( '/dev/ttyAMA0', controller, 2)
cmdT = serialThread.cmdThread()
httpT = httpThread.httpThread(1,2)

serialT.start()
httpT.start()
cmdT.start()

print "Type CTRL-C to quit..."

signal.signal(signal.SIGINT, sigint_handler)

#line = ''

while not bExit:
	time.sleep(1)

print "Stopping tasks"
cmdT.stop()
httpT.stop()
serialT.stop()

# send a redis publish to kick cmdT
redis = redis.StrictRedis( host='localhost', port=6379, db=0)
redis.publish("poolcmd", "EXIT" )

print "Joining serial task..."
serialT.join()
print "Joining command task..."
cmdT.join()
print "Joining http task..."
httpT.join()

print "CTRL-C pressed, exiting (hopefully)"
sys.exit(0)
