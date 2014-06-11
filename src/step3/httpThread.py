#!/usr/bin/python

import threading
import thread
import time

class httpThread (threading.Thread):
	def __init__(self):
		self.p1 = p1
		self.p2 = p2
		self.exit = False
		threading.Thread.__init__(self)

	def stop(self):
		self.exit = True

	def run(self):
		while self.exit == False:
			print "http tick"
			sleep(1)
