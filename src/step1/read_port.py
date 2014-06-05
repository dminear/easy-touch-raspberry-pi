#!/usr/bin/python

import serial
import time
import sys
import hexdump

ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=0)

while True:
  # ser.write("hello")
  s = ser.read(32)
  hexdump.hexdump( s )
  #for i in range(0,len(s)):
  #  c = s[i]
  #  print "%#04x" % ord(c)
  time.sleep(0.5)


