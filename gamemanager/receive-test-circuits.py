#!/usr/bin/env python

from circuits import Component, Debugger, Event, handler
from circuits.io.serial import Serial
#from time import sleep

class helloEv(Event):
    """hello Event"""

class SerInput(Component):
    def __init__(self, device = '/dev/ttyUSB0'):
        super(SerInput, self).__init__()
        Serial(device).register(self)
    
    def read(self, data):
        print ('Received: %r' % data)
        self.fire(TestEv('hallo'))

    def started(self, c):
        self.fire(helloEv())
        #raise SystemExit(0)
    
    def helloEv(self):
        print ('test')

if __name__ == "__main__":        

    (SerInput(device = '/dev/ttyUSB0') + Debugger()).run()
    ''' + Debugger() + TT()
    d.run()'''
