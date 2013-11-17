""" LOGGING """

from circuits import Component
from datetime import datetime

class Logger(Component):
    def game_initialized(self, state):
        print "Logger started."
        filename = datetime.now().strftime("%Y-%m-%d--%H:%M.dartlog")
        self.file = open(filename, 'w')
        self.file.write("Players: %s\n" % (' '.join(state.players)))

    def round_finished(self, state):
        self.file.write("%s: %s\n" % (state.players[state.currentPlayer], ' '.join(state.currentDarts)))
