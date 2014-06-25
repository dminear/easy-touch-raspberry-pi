#!/usr/bin/python

import sys
import hashlib
import redis

print "Enter the password to set: "
pw = sys.stdin.readline().strip()
h = hashlib.md5()
m = h.update(pw)
s = h.hexdigest()
print "hex string is %s" % s
print "storing to database"
r = redis.StrictRedis( host='localhost', port=6379, db=0)
r.hset( "pool", "password", s )
print "done"
