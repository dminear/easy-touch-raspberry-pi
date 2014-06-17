#!/usr/bin/python

import redis
import controller

servAddr = ('', 8080)

httpcontroller = controller.controller( [] )
httpcontroller.load()		# from redis

httpr = redis.StrictRedis( host='localhost', port=6379, db=0)

print( "<p>Air temp is %d</p>" % ( int(httpcontroller.getairtemp())))
print( "<p>Pool temp is %d</p>" % ( int(httpcontroller.getpooltemp())))
print( "<p>Spa temp is %d</p>" % ( int(httpcontroller.getspatemp())))
cl = httpcontroller.getcircuitlist()
state = ['OFF', 'ON']
for c in cl:
	print("%s circuit %s is %s</br>" % (c.getName(), c.getNumber(), state[int(c.getState())]))

# test to send back command from http thread
httpr.publish("poolcmd", "NOP")

