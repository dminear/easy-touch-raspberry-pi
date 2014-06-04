#! /usr/bin/python

import time
import serial
import string
import sys
import os

circuitStr=sys.argv[1]
stateStr=sys.argv[2]

## Set Pi GPIO 23 as an output and set to 1 so RS485 tranceiver is driving RS485 bus
os.system("/usr/local/bin/gpio mode 4 out")
os.system("/usr/local/bin/gpio write 4 1")
time.sleep(1)

output = " "
ser = serial.Serial('/dev/ttyAMA0', baudrate=9600, timeout=3)

## padding
pad=chr(0xFF)+chr(0xFF)+chr(0xFF)+chr(0xFF)
## header
pad2=chr(0x00)+chr(0xFF)

#header
bytes=[0xA5,0x27]
#bytes=[0xA5,0x01]

## src dest
bytes.append(0x10)
bytes.append(0x20)
bytes.append(0x86)
bytes.append(0x02)

## pool default case
circuit=0x00
if circuitStr=="filter":
        circuit=0x01
if circuitStr=="cleaner":
	circuit=0x02
if circuitStr=="light":
	circuit=0x03
if circuitStr=="lowspeed":
	circuit=0x04



bytes.append(circuit)

#state
state=0x00
if (stateStr=="ON"):
	state=0x01

bytes.append(state)

print circuitStr,",",circuit,",",stateStr,",",state

##checksum
sum=0;
byteStr=""
for b in bytes:
        sum=sum+b
	byteStr=byteStr+chr(b)

chksum= [0xff&sum>>i for i in 8,0]
print chksum

for c in chksum:
	byteStr=byteStr+chr(c)


## padding
ser.write(pad2+byteStr)
time.sleep(3)

## Set tranceiver as a receiver so other equipment can drive RS485 bus
os.system("/usr/local/bin/gpio write 4 0")


