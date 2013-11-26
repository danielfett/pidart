""" LOGGING """

from circuits import Component
from datetime import datetime

class Logger(Component):
    def GameInitialized(self, state):
        print ("Logger started.")
        filename = "%s.dartlog" % state.id
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


import sqlite3

class DetailedLogger(Component):
    def started(self, x):
        self.conn = sqlite3.connect('darts.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS games (id TEXT, startvalue INT, date DATETIME)''')
        self.cursor.execute('''CREATE UNIQUE INDEX IF NOT EXISTS index_id ON games (id)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS throws (games_id TEXT, player TEXT, frame TEXT, dart TEXT, code TEXT, before INT, timestamp DATETIME)''')
        self.cursor.execute('''CREATE UNIQUE INDEX IF NOT EXISTS index_throws ON throws (games_id, player, frame, dart)''')
        self.cursor.execute('''CREATE INDEX IF NOT EXISTS index_results ON throws (player, before)''')
        self.cursor.execute('''PRAGMA synchronous = OFF''')
        self.cursor.execute('''PRAGMA journal_mode = MEMORY''')
        self.conn.commit()
    
    def GameInitialized(self, state):
        args = (
            state.id,
            state.startvalue
            )
        self.cursor.execute('INSERT INTO games (id, startvalue, date) VALUES (?, ?, CURRENT_TIMESTAMP)', args)
        self.conn.commit()

    @handler('Hit', priority=-1)
    def Hit(self, state, code):
        args = (
            state.id,
            state.currentPlayer.name,
            len(state.currentPlayer.history),
            len(state.currentDarts),
            code,
            state.currentPlayer.score - state.currentScore
            )
        print "%r %r %r %r %r %r" % args
        self.cursor.execute('INSERT INTO throws (games_id, player, frame, dart, code, before, timestamp) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)', args)

    def FrameFinished(self, state):
        self.conn.commit()
