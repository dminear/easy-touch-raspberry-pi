#!/usr/bin/python

import threading
import thread
import time
import redis
import controller
import BaseHTTPServer, cgi
import json

servAddr = ('', 8080)

httpcontroller = controller.controller( [] )
httpcontroller.load()		# from redis

httpr = redis.StrictRedis( host='localhost', port=6379, db=0)

class httpServHandler( BaseHTTPServer.BaseHTTPRequestHandler):
	def do_GET(self):
		if self.path.find('?') != -1:
			self.path, self.query_string = self.path.split('?',1)
		else:
			self.query_string = ''
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()

		# set up global environment
		self.globals = dict(cgi.parse_qsl(self.query_string))
	
		# redirect output to browser
		#sys.stdout = self.wfile	

		# execute script
		self.wfile.write("<html><head><title>Pool Controller</title></head><body>")
		self.wfile.write("<h2>Pool Controller</h2>")
		self.wfile.write("<p>Executing %s </p>" % (self.path))
		self.wfile.write("<p>with globals %s<hr>" % (self.globals))
		#execfile(self.path, self.globals)
			

		self.wfile.write( "<p>Air temp is %d</p>" % ( int(httpcontroller.getairtemp())))
		self.wfile.write( "<p>Pool temp is %d</p>" % ( int(httpcontroller.getpooltemp())))
		self.wfile.write( "<p>Spa temp is %d</p>" % ( int(httpcontroller.getspatemp())))
		cl = httpcontroller.getcircuitlist()
		state = ['OFF', 'ON']
		for c in cl:
			self.wfile.write("%s circuit %s is %s</br>" % (c.getName(),
									c.getNumber(), 
									state[int(c.getState())]))
		
		self.wfile.write( "</body></html>" )

		# test to send back command from http thread
		httpr.publish("poolcmd", "NOP")



class httpThread (threading.Thread):
	def __init__(self, p1, p2):
		self.p1 = p1
		self.p2 = p2
		self.exit = False
		threading.Thread.__init__(self)

	def stop(self):
		#self.serv.server_close()
		self.exit = True

	def run(self):
		serv = BaseHTTPServer.HTTPServer( servAddr, httpServHandler )
		while self.exit == False:
			serv.serve_forever()


