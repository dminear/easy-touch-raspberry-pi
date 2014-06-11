#!/usr/bin/python

import serialThread
import httpThread
import time

serialT = serialThread.serialThread( '/dev/ttyAMA0', 1, 2)
httpT = httpThread.httpThread(1,2)

serialT.start()
httpT.start()

time.sleep(10)

serialT.stop()
httpT.stop()

