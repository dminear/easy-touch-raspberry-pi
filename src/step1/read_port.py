#!/usr/bin/python

import serial
import time

ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=0)

while True:
  ser.write("hello")
  s = ser.read(40)
  print s
  time.sleep(1)


