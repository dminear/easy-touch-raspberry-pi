#!/usr/bin/python

import redis
import controller
import cgi
import sys
import json as jsonmod
import circuit

httpcontroller = controller.controller( [] )
httpcontroller.load()		# from redis
httpr = redis.StrictRedis( host='localhost', port=6379, db=0)

# jquery is available at /js/jquery.js

if 'method' in globals() and method == 'GET':
	print '["Invalid GET request. You need to POST."]'
else:
	# check for json POST
	if 'json' in globals():
		json = 1
	else:
		json = 0;

	if json == 1:
		# take json input and convert to object
		params = jsonmod.loads(query_string)
		updatecontroller = controller.controller([])
		for i in params.keys():
			if i == "spasettemp":
				updatecontroller.setspasettemp( params[i] )
			elif i == "poolsettemp":
				updatecontroller.setpoolsettemp( params[i] )
			elif i == "airtemp":
				updatecontroller.setairtemp( params[i] )
			elif i[:7] == "circuit":	# build circuit
				cir = circuit.circuit( i[7:],
							params[i]['name'],
							params[i]['byte'],
							params[i]['bit'],
							params[i]['value'] )
				updatecontroller.appendcircuit( cir );
			elif i == "token":
				updatecontroller.setpassword( params[i] )
			else:
				# nothing, ignore
				a = 1
	else:
		# take input and convert to object
		if 'query_string' in globals():
			params = dict(cgi.parse_qsl(query_string))
		else:
			params = {}

		# if a key does not exist, then we will assume it is a "0"
		# this is done because a browser will only send back the
		# checkboxes that are CHECKED.  It is possible that the
		# user UNCHECKED a box, in which case it will not be sent
		# back in the query string.

		for i in range(17):
			v = "circuit%d" % (i)
			if v in params:
				# do nothing
				a = 1
			else:
				# add to dict
				params[v] = "0"

		# just build a controller with what we got. Fake out the byte
		# and bit and name; we only want values for now to compare
		# with the real controller
		
		updatecontroller = controller.controller([])

		for i in params.keys():
			if i == "spasettemp":
				updatecontroller.setspasettemp( params[i] )
			elif i == "poolsettemp":
				updatecontroller.setpoolsettemp( params[i] )
			elif i == "airtemp":
				updatecontroller.setairtemp( params[i] )
			elif i[:7] == "circuit":	# build circuit
				cir = circuit.circuit( i[7:], i, 0, 0, params[i] )
				updatecontroller.appendcircuit( cir );
			elif i == "token":
				updatecontroller.setpassword( params[i] )
			else:
				# nothing, ignore
				a = 1

	# check passwords
	if updatecontroller.getpassword() != httpcontroller.getpassword():
		# failed, return bad response
		if json == 1:
			print '["failed"]'
		else:
			print '<html><head><title>Failed</title></head><body><p>update failed</p><a href="/">Back to status</a></body></html>'
	else:	# good password	
		if json == 1:
			print '["success"]'
		else:
			print '<html><head><title>Response</title></head><body><p>update success</p><a href="/">Back to status</a></body></html>'
			
		# Need to take updatecontroller
		# and bounce against a real controller and find the deltas to
		# send as commands.

		# check setpoints for differences
		if int(httpcontroller.getpoolsettemp()) != int(updatecontroller.getpoolsettemp()):
			httpr.publish("poolcmd", "SET POOLTEMP %s" % (updatecontroller.getpoolsettemp()))
		
		if int(httpcontroller.getspasettemp()) != int(updatecontroller.getspasettemp()):
			httpr.publish("poolcmd", "SET SPATEMP %s" % (updatecontroller.getspasettemp()))
		
	
		# check circuits for differences
		for c in httpcontroller.getcircuitlist():
			if c.getState() != updatecontroller.getcircuitnumstate(c.getNumber()):
				# we got a difference
				httpr.publish("poolcmd", "SET CIRCUIT %s %s" % (c.getNumber(), 1-int(c.getState()) ))

