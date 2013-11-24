""" LOGGING """

from circuits import Component
from datetime import datetime

class Logger(Component):
    def GameInitialized(self, state):
        print ("Logger started.")
        filename = datetime.now().strftime("%Y-%m-%d--%H:%M.dartlog")
        self.file = open(filename, 'w')
        self.file.write("Players:%s " % (','.join([p.name for p in state.players])))

    def Hit(self, state, code):
        self.file.write('%s ' % code)

    def HitBust(self, state, code):
        self.file.write('%s (busted) ' % code)

    def HitWinner(self, state, code):
        self.file.write('%s (checkout) ' % code)

    def FrameStarted(self, state):
        self.file.write('| (%s) ' % state.currentPlayer.name)
