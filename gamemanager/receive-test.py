#!/usr/bin/python

import serial
from time import sleep
from codes import FIELDCODES

DEVICE = '/dev/ttyACM0'

ser = serial.Serial(DEVICE, 115200)
#sleep(1) # for arduino
while True:
    print "%x" % ord(ser.read(1))
    byte = ord(ser.read(1))
    if byte in FIELDCODES.keys():
        print FIELDCODES[byte]
    else:
        print "Unknown: %d" % byte
