from circuits import Component, Event
from events import ReceiveInput, StartGame
from circuits.io import Serial, File, Process
from codes import FIELDCODES
from time import sleep


class FireInput(Event):
    pass

class DartInput(Component):
    channel = 'serial'

    def __init__(self, device):
        super(DartInput, self).__init__()
        Serial(device, 
               baudrate = 115200, 
               bufsize = 1, 
               timeout = 0).register(self)
        print "Reading from serial device %s" % device
        
    def read(self, data):
        for b in data:
            inp = ord(b)
            try:
                self.fire(ReceiveInput('code', FIELDCODES[inp]))
                self.flush()
            except KeyError:
                raise Exception("Unknown fieldcode: %x" % inp)

class FileInput(Component):
    def __init__(self, f, delay = 3, test = False):
        super(FileInput, self).__init__()
        with open(f, 'r') as infile:
            self.data = infile.read().split(' ')
        players = self.data[0].split(':')[1].split(',')
        self.fire(StartGame(players, 301, test))
        self.pointer = None
        self.delay = delay

    def GameInitialized(self, *args):
        self.pointer = 1
    
    def generate_events(self, *args):
        if self.pointer != None and self.pointer < len(self.data):
            s = self.data[self.pointer]
            while s.startswith('('): # this is a comment, so ignore.
                self.pointer += 1
                s = self.data[self.pointer]
            if s == '|': # next player
                self.fire(ReceiveInput('generic', 'next_player'))
            else:
                self.fire(ReceiveInput('code', s))
            self.pointer += 1
        elif self.pointer >= len(self.data):
            self.unregister()


'''
class FakeInput(object):
    def read(self):
        inp = raw_input("? ").strip().upper()
        return inp
'''
