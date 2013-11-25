from circuits import Component
from events import ReceiveInput
from circuits.io.serial import Serial
from circuits.io.file import File
from codes import FIELDCODES


class DartInput(Component):
    channel = 'serial'

    def __init__(self, device):
        super(DartInput, self).__init__()
        Serial(device, 
               baudrate = 115200, 
               bufsize = 1, 
               timeout = 0).register(self)
        
    def read(self, data):
        for b in data:
            inp = ord(b)
            try:
                self.fire(ReceiveInput('code', FIELDCODES[inp]))
                self.flush()
            except KeyError:
                raise Exception("Unknown fieldcode: %x" % inp)

class FileInput(Component):
    def __init__(self, f):
        super(FileInput, self).__init__()
        with open(f, 'r') as infile:
            self.data = infile.read().split(' ')
        players = self.data[0].split(':')[1].split(',')
        self.fire(StartGame(players))

    def GameInitialized(self, state):
        for s in self.data[1:]:
            if s.startswith('('): # this is a comment, so ignore.
                pass
            elif s == '|': # next player
                self.fire(ReceiveInput('generic', 'next_player'))
            else:
                self.fire(ReceiveInput('code', s))


'''
class FakeInput(object):
    def read(self):
        inp = raw_input("? ").strip().upper()
        return inp
'''
