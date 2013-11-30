#!/usr/bin/python

import serial
from time import sleep
from codes import FIELDCODES


if __name__ == "__main__":
    DEVICE = '/dev/ttyACM0'

    ser = serial.Serial(DEVICE, 115200)
    #sleep(1) # for arduino
    while True:
        byte = ord(ser.read(1))
        if byte in FIELDCODES.keys():
            x = FIELDCODES[byte]
            print x, "INNNER" if x.endswith('i') else ''
        else:
            print "Unknown: %d" % byte
