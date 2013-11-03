#!/usr/bin/python

import serial
from time import sleep

DEVICE = '/dev/ttyACM0'

FIELDCODES = { # just some example values for now
    0: 'T20',
    1: 'D20',
    2: 'S20',
    16: 'T10',
    17: 'D10',
    32: 'T5',
    33: 'D5'}

ser = serial.Serial(DEVICE, 115200)
sleep(1) # for arduino
while True:
    byte = ord(ser.read(1))
    if byte in FIELDCODES.keys():
        print FIELDCODES[byte]
    else:
        print "Unknown: %d" % byte
