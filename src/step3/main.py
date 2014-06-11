#!/usr/bin/python

import serialThread
import httpThread
import time

serialThread = serialThread( '/dev/ttyAMA0', 1, 2)
httpThread = httpThread()

serialThread.start()
httpThread.start()


sleep(10)

serialThread.stop()

