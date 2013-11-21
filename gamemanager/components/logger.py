""" LOGGING """

from circuits import Component
from datetime import datetime

class Logger(Component):
    def game_initialized(self, state):
        print "Logger started."
        filename = datetime.now().strftime("%Y-%m-%d--%H:%M.dartlog")
        self.file = open(filename, 'w')
        self.file.write("Players:%s " % (','.join(state.players)))

    def hit(self, state, code):
        self.file.write('%s ' % code)

    def hit_bust(self, state, code):
        self.file.write('%s (busted) ' % code)

    def hit_winner(self, state, code):
        self.file.write('%s (checkout) ' % code)

    def frame_started(self, state):
        self.file.write('| (%s) ' % state.players[state.currentPlayer])
