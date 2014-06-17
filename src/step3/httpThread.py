#!/usr/bin/python

import threading
import thread
import BaseHTTPServer, cgi
import sys
import os.path

servAddr = ('', 8080)


#
# The HTTP code snippet is from "Python PHRASEBOOK" by Brad Dayley copyright
#  2007 by Sams Publishing.  It is a good little book that seems to have
# enough of what you need to do something, and then you can check the python
# docs for more.
#

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
		stdsave = sys.stdout
		sys.stdout = self.wfile	

		# execute script
		self.wfile.write("<html><head><title>Pool Controller</title></head><body>")
		self.wfile.write("<h2>Pool Controller</h2>")
		if self.path == "" or self.path == "/":
			self.path = "index.py"
			print "path is ", self.path

		# check that file is there before running
		if os.path.isfile(self.path):
			self.wfile.write("<p>Executing %s </p>" % (self.path))
			self.wfile.write("<p>with globals %s<hr>" % (self.globals))
			execfile(self.path, self.globals)
		else:
			self.wfile.write("script %s not found" % (self.path))

		self.wfile.write( "</body></html>" )

		# test to send back command from http thread
		sys.stdout = stdsave	# put back



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


