#!/usr/bin/python

import serialThread
import httpThread
import time

serialT = serialThread.serialThread( '/dev/ttyAMA0', 1, 2)
httpT = httpThread.httpThread(1,2)

serialT.start()
httpT.start()

bExit = False

while not bExit:
	try: 
		time.sleep(1)
	except:
		bExit=True

serialT.stop()
httpT.stop()

