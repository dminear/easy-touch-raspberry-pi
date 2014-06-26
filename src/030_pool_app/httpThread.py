#!/usr/bin/python

import threading
import thread
import BaseHTTPServer, cgi
import sys
import os.path
import os

servAddr = ('', 8000)

mimedict = { 	"js" : "application/javascript",
		"txt" : "text/plain",
		"html" : "text/html",
		"css" : "text/css"
	}


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

		# set up global environment
		self.globals = dict(cgi.parse_qsl(self.query_string))
		self.globals["method"] = "GET"
	
		# execute script
		if self.path == "" or self.path == "/":
			self.path = "/index.py"
	
		self.path = self.path[1:]	# strip off leading /

		# check that file is there before running
		if os.path.isfile(self.path) and self.path[-2:] == "py":
			# run the script
			self.send_response(200)
			try:
				if self.globals["json"]:
					type = 'application/json'
				else:
					type = 'text/html'
			except:
				type = 'text/html'
			self.send_header('Content-type', type)
			self.end_headers()

			# redirect output to browser
			stdsave = sys.stdout
			sys.stdout = self.wfile	
			#self.wfile.write("<p>Executing %s </p>" % (self.path))
			#self.wfile.write("<p>with globals %s<hr>" % (self.globals))
			execfile(self.path, self.globals)
			sys.stdout = stdsave	# put back

		elif os.path.isfile(self.path):
			# find mime type
			if self.path.find('.') != -1:
				filename, ext = self.path.split('.',1)
			else:
				ext = "txt"
			# a existing file, just send it
			self.send_response(200)
			self.send_header('Content-type', mimedict[ext])
			self.end_headers()
			infile = open(self.path, "r")
			self.wfile.write( infile.read() )
			infile.close()
		else:	# not found
			self.send_response(404)
			self.send_header('Content-type', 'text/html')
			self.end_headers()
			infile = open("404", "r")
			self.wfile.write( infile.read() )
			infile.close()

	def do_POST(self):
		if self.path.find('?') != -1:
			self.path, parms = self.path.split('?',1)
		else:
			parms = ''

		self.query_string = self.rfile.read(int(self.headers['Content-Length']))
		self.args = dict(cgi.parse_qsl(self.query_string))

		urlparms = dict(cgi.parse_qsl(parms))

		try:
			if urlparms['json']:
				jsonrequest = True
				self.args["json"] = 1
		except:
			jsonrequest = False

		# add key for benefit of called script
		self.args["method"] = "POST"

		self.path = self.path[1:]	# strip off leading /
		# so it is available to the called script
		self.args["query_string"] = self.query_string

		'''
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()
		self.wfile.write('<html><head><title>Post page</title></head><body>')

		self.wfile.write("<p>Location is %s</p>" % (self.path))
		self.wfile.write("<p>args are %s</p>" % (self.args))

		self.wfile.write("</pre>")
		self.wfile.write('</body></html>')

'''
		# check that file is there before running
		if os.path.isfile(self.path) and self.path[-2:] == "py":
			# run the script
			self.send_response(200)
			if jsonrequest:
				self.send_header('Content-type', 'application/json')
			else:
				self.send_header('Content-type', 'text/html')
			self.end_headers()
			# redirect output to browser
			stdsave = sys.stdout
			sys.stdout = self.wfile	
			execfile(self.path, self.args)
			sys.stdout = stdsave	# put back
		else:	# not found
			self.send_response(404)
			self.send_header('Content-type', 'text/html')
			self.end_headers()
			infile = open("404", "r")
			self.wfile.write( infile.read() )
			infile.close()

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
		os.chdir('web')
		serv = BaseHTTPServer.HTTPServer( servAddr, httpServHandler )
		while self.exit == False:
			serv.serve_forever()


