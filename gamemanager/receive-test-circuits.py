from circuits import Component, Debugger
from circuits.io.serial import Serial

class SerInput(Component):
    def __init__(self, device = '/dev/ttyUSB0'):
        super(SerInput, self).__init__()
        Serial(device, baudrate = 115200, bufsize = 1, timeout = 0, channel = 'serial').register(self)
    
    def read(self, data):
        print 'Received: %r' % data

d = SerInput(device = '/dev/ttyACM0') + Debugger()
d.run()
