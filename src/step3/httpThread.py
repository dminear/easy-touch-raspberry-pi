#!/usr/bin/python

import threading
import thread
import time
import redis

class httpThread (threading.Thread):
	def __init__(self, p1, p2):
		self.p1 = p1
		self.p2 = p2
		self.exit = False
		self.r = redis.StrictRedis( host='localhost', port=6379, db=0)
		threading.Thread.__init__(self)

	def stop(self):
		self.exit = True

	def run(self):
		while self.exit == False:
			#print "http tick"
			time.sleep(1)
			self.r.publish("poolcmd", "NOP")

