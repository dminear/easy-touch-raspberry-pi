#!/usr/bin/python

import sys
import hashlib

print "Enter the password to set: "

pw = sys.stdin.readline()

print "pw is %s" % pw

h = hashlib.md5()

m = h.update(pw)

s = h.hexdigest()

print "hex string is %s" % s

