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
	print '<html> <head> <title>Pool Controller</title> '
	print '<link rel="stylesheet" type="text/css" href="static/style.css">'
	#print '<link rel="stylesheet" href="js/jquery-ui.css">'
	#print '<script src="js/jquery.js"></script>'
	#print '<script src="js/jquery-ui.js"></script>'
	print '</head> <body>'

	print '<form name="input" method="post" action="change.py">'

	#print '<div id="slider"></div>'

	print '<span>Air temperature is %d &deg;F</span></br>' % ( int(httpcontroller.getairtemp()))
	print '<span>Water temperature is %d &deg;F</span></br>' % ( int(httpcontroller.getwatertemp()))
	print '<span>Pool Set Temperature: <input type="text" size="4" name="poolsettemp" value="%s">&deg;F</span></br>' % (httpcontroller.getpoolsettemp())
	print '<span>Spa Set Temperature: <input type="text" size="4" name="spasettemp" value="%s">&deg;F</span></br>' % (httpcontroller.getspasettemp())

	cl = httpcontroller.getcircuitlist()
	for c in cl:
		if c.getState() == "1":
			val = "CHECKED"
		else:
			val = ""
		print( '<span><input type="checkbox" name="circuit%s" value="1" %s>%s</span></br>' % ( c.getNumber(), val, c.getName().capitalize() ))
	print '<span>Token: <input type="text" size="32" name="token"></span></br>'
	print '<span>Wall time %s, Pool time %s</span></br>' % (httpcontroller.getwallclocktime(), httpcontroller.getpoolclocktime())
	print '<input type="submit" value="Submit"> </form>'

	#print '<script> $( "#slider" ).slider(); </script>'

	print '</body></html>'
