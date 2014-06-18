#!/usr/bin/python

import redis
import controller
import cgi

servAddr = ('', 8080)

httpcontroller = controller.controller( [] )
httpcontroller.load()		# from redis

httpr = redis.StrictRedis( host='localhost', port=6379, db=0)

# jquery is available at /js/jquery.js

print '''
<html>
<head>
<title>Pool Controller</title>
</head>
<body>

<h2>Pool Controller</h2>
'''

print( "<p>Air temp is %d</p>" % ( int(httpcontroller.getairtemp())))
print( "<p>Pool temp is %d</p>" % ( int(httpcontroller.getpooltemp())))
print( "<p>Spa temp is %d</p>" % ( int(httpcontroller.getspatemp())))
cl = httpcontroller.getcircuitlist()
state = ['OFF', 'ON']
for c in cl:
	print("%s circuit %s is %s</br>" % (c.getName(), c.getNumber(), state[int(c.getState())]))

print '''
<hr>
<form name="input" method="post" action="change.py">
'''
print '<span>Pool Temperature: <input type="text" name="pooltemp" value="%s"></span></br>' % (httpcontroller.getpooltemp())
print '<span>Spa Temperature: <input type="text" name="spatemp" value="%s"></span></br>' % (httpcontroller.getspatemp())

for c in cl:
	print( '<span><input type="checkbox" name="circuit%s" value="%s">%s</span></br>' % ( c.getNumber(), c.getState(), c.getName().capitalize() ))

print '''
<input type="submit" value="Submit">
</form>
</body></html>
'''

# test to send back command from http thread
httpr.publish("poolcmd", "NOP")

