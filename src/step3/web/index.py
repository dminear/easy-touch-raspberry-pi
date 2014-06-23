#!/usr/bin/python

import redis
import controller
import cgi
import sys
import json as jsonmod

httpcontroller = controller.controller( [] )
httpcontroller.load()		# from redis

httpr = redis.StrictRedis( host='localhost', port=6379, db=0)

# jquery is available at /js/jquery.js

try:
	if globals()['json']:
		# build dictionary
		d = {"airtemp" : int(httpcontroller.getairtemp()),
			"watertemp" : int(httpcontroller.getwatertemp()),
			"spasettemp" :  int(httpcontroller.getspasettemp()),
			"poolsettemp" :  int(httpcontroller.getpoolsettemp()),
			}
		cl = httpcontroller.getcircuitlist()
		for c in cl:
			d["circuit%s" % (c.getNumber())] = c.todict()

		print jsonmod.dumps(d)

except:		# json not defined, give a text/html response
	print '<html> <head> <title>Pool Controller</title> </head> <body>'
	print '<form name="input" method="post" action="change.py">'
	print '<span>Air temp is %d</span></br>' % ( int(httpcontroller.getairtemp()))
	print '<span>Water temp is %d</span></br>' % ( int(httpcontroller.getwatertemp()))
	print '<span>Pool Set Temperature: <input type="text" name="pooltemp" value="%s"></span></br>' % (httpcontroller.getpoolsettemp())
	print '<span>Spa Set Temperature: <input type="text" name="spatemp" value="%s"></span></br>' % (httpcontroller.getspasettemp())

	cl = httpcontroller.getcircuitlist()
	for c in cl:
		if c.getState() == "1":
			val = "CHECKED"
		else:
			val = ""
		print( '<span><input type="checkbox" name="circuit%s" value="1" %s>%s</span></br>' % ( c.getNumber(), val, c.getName().capitalize() ))

	print '<input type="submit" value="Submit"> </form> <hr>'
	print 'Air temp is %d</br>' % ( int(httpcontroller.getairtemp()))
	print 'Water temp is %d</br>' % ( int(httpcontroller.getwatertemp()))
	state = ['OFF', 'ON']
	for c in cl:
		print "%s circuit %s is %s</br>" % (c.getName(), c.getNumber(), state[int(c.getState())])
	print '</body></html>'
