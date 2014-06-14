""" LOGGING """

from circuits import Component, handler
from datetime import datetime
from os.path import join
from tempfile import TemporaryFile, NamedTemporaryFile
import sqlite3

LOG_ROOT = 'logs'

class Logger(Component):
    def __init__(self, test=False):
        Component.__init__(self)
        self.test = test
        self.file = None

    def finish(self):
        if self.file is None:
            return
        self.file.close()

    def GameInitialized(self, state):
        print ("Logger started.")
        self.finish()
        if state.testgame or self.test:
            self.file = TemporaryFile()
        else:
            filename = join(LOG_ROOT, "%s.dartlog" % state.id)
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

    def GameOver(self, state, *args):
        self.finish()


class DetailedLogger(Component):
    def __init__(self, test=False):
        Component.__init__(self)
        if test:
            self.file = NamedTemporaryFile()
            self.filename = self.file.name
        else:
            self.filename = join(LOG_ROOT, 'darts.db')

    def started(self, x):
        self.conn = sqlite3.connect(self.filename)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS games (id TEXT, startvalue INT, date DATETIME)''')
        self.cursor.execute('''CREATE UNIQUE INDEX IF NOT EXISTS index_id ON games (id)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS throws (games_id TEXT, player TEXT, frame TEXT, dart TEXT, code TEXT, before INT, timestamp DATETIME)''')
        self.cursor.execute('''CREATE UNIQUE INDEX IF NOT EXISTS index_throws ON throws (games_id, player, frame, dart)''')
        self.cursor.execute('''CREATE INDEX IF NOT EXISTS index_results ON throws (player, before)''')
        self.cursor.execute('''PRAGMA synchronous = OFF''')
        self.cursor.execute('''PRAGMA journal_mode = MEMORY''')
        self.conn.commit()
    
    @handler('GameInitialized', priority=-1)
    def GameInitialized(self, state):
        if state.testgame:
            return
        args = (
            state.id,
            state.startvalue
            )
        print "%r" % (args,)
        self.cursor.execute('BEGIN TRANSACTION')
        self.cursor.execute('INSERT INTO games (id, startvalue, date) VALUES (?, ?, CURRENT_TIMESTAMP)', args)

    @handler('Hit', 'HitWinner', 'HitBust', priority=-1)
    def Hit(self, state, code):
        if state.testgame:
            return
        args = (
            state.id,
            state.currentPlayer.name,
            len(state.currentPlayer.history),
            len(state.currentDarts),
            code,
            state.currentPlayer.score - state.currentScore
            )
        self.cursor.execute('INSERT INTO throws (games_id, player, frame, dart, code, before, timestamp) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)', args)

    @handler('GameOver', 'HitWinner', priority=-1)
    def GameOver(self, state, *args):
        if state.testgame:
            return
        self.conn.commit()

    def get_num_rows(self):
        self.conn.close()
        self.conn = sqlite3.connect(self.filename)
        self.cursor = self.conn.cursor()
        
        self.cursor.execute('SELECT count(*) FROM games')
        num_games = self.cursor.fetchone()[0]
        self.cursor.execute('SELECT count(*) FROM throws')
        num_throws = self.cursor.fetchone()[0]
        return (num_games, num_throws)
        
        
