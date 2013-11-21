from circuits import Component, Debugger
from circuits.io.serial import Serial
from time import sleep

class SerInput(Component):
    def __init__(self, device = '/dev/ttyUSB0'):
        super(SerInput, self).__init__()
        Serial(device).register(self)
    
    def read(self, data):
        print ('Received: %r' % data)

d = SerInput(device = '/dev/ttyACM0') + Debugger()
d.run()
