#!/usr/bin/python

import threading
import thread
import BaseHTTPServer, cgi
import sys
import os.path
import os

servAddr = ('', 8080)

mimedict = { 	"js" : "application/javascript",
		"txt" : "text/plain",
		"html" : "text/html"
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
	
		# execute script
		if self.path == "" or self.path == "/":
			self.path = "/index.py"
	
		self.path = self.path[1:]	# strip off leading /

		# check that file is there before running
		if os.path.isfile(self.path) and self.path[-2:] == "py":
			# run the script
			self.send_response(200)
			self.send_header('Content-type', 'text/html')
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
			self.path, self.query_string = self.path.split('?',1)
		else:
			self.query_string = ''

		# set up global environment
		self.globals = dict(cgi.parse_qsl(self.query_string))
	
		# execute script
		if self.path == "" or self.path == "/":
			self.path = "/index.py"
	
		self.path = self.path[1:]	# strip off leading /

		
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()
		self.wfile.write('<html><head><title>Post page</title></head><body>')
		
		self.wfile.write("<pre>")

		#self.wfile.write( self.rfile.read() )

		self.wfile.write("</pre>")
		self.wfile.write('</body></html>')

'''
		# check that file is there before running
		if os.path.isfile(self.path) and self.path[-2:] == "py":
			# run the script
			self.send_response(200)
			self.send_header('Content-type', 'text/html')
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
'''


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


