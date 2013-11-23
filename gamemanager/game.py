#!/usr/bin/python

from codes import FIELDCODES
from time import sleep
from sys import exit
from circuits import Component, Event, Debugger, handler
from circuits.io.serial import Serial
from circuits.io.file import File
from copy import deepcopy
import argparse
from events import *

from components.webserver import Webserver
from components.logger import Logger



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
     
'''
class FakeInput(object):
    def read(self):
        inp = raw_input("? ").strip().upper()
        return inp
'''

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
                


""" MAIN COMPONENT """

from operator import itemgetter

class GameState(object):
    def __init__(self, players, startvalue):
        self.state = None
        self.players = players
        self.scores = {}
        self.history = {}

        for i in range(len(self.players)):
            self.scores[i] = startvalue
            self.history[i] = []

        self.currentPlayer = 0
        self.currentDarts = []
        self.currentScore = 0
        self.skippedPlayers = []
        self.skipOrder = []

    def add_dart(self, dart, s):
        self.currentDarts.append(dart)
        self.currentScore += s
        if self.scores[self.currentPlayer] - self.currentScore < 0:
            return 'bust'
        if self.scores[self.currentPlayer] - self.currentScore ==  0:
            return 'winner'

    def flush_frame(self):
        print "flushing with score = %d and current score %d" % (self.scores[self.currentPlayer], self.currentScore)
        result = self.scores[self.currentPlayer] - self.currentScore
        if result >= 0:
            self.scores[self.currentPlayer] = result
            text = "%d" % self.currentScore
        elif result == 0:
            text = "checked out"
        else: # result < 0:
            text = "bust"
        self.history[self.currentPlayer].append({'text': text, 'darts': self.currentDarts})
        self.currentDarts = []
        self.currentScore = 0

    def cancel_frame(self):
        self.currentDarts = []
        self.currentScore = 0

    def next_frame(self):
        # todo: if there exists a player who has not checked out yet, but has played less frames than the worst player that checked out already, this player may continue playing.
        nextPlayer = None
        winners = self.winners()
        # first check if we can find the next player without considering the skipped ones
        for p in range(len(self.players)):
            if p in self.skippedPlayers or p in winners:
                continue
            if nextPlayer == None or len(self.history[p]) < len(self.history[nextPlayer]):
                nextPlayer = p
        # now check the skipped players
        if nextPlayer == None and len(self.skippedPlayers):
            for p in range(len(self.players)):
                if p in winners:
                    continue
                if nextPlayer == None or len(self.history[p]) < len(self.history[nextPlayer]):
                    nextPlayer = p
            self.toggle_skip(nextPlayer)
        if nextPlayer == None:
            return False # todo: check these values somewhere.
        self.currentPlayer = nextPlayer
        return True

    def toggle_skip(self, player):
        if player in self.skippedPlayers:
            self.skippedPlayers.remove(player)
            return False
        else:
            self.skippedPlayers.append(player)
            return True
        
    def winners(self):
        return [x for x in range(len(self.players)) if self.scores[x] == 0]

    def game_over(self):
        return len(self.winners()) == len(self.players) - 1

    def player_list(self, sortby = 'started'):
        lst = [{
                'started': x, 
                'frames': len(self.history[x]), 
                'last_frame': (self.history[x][-1] if len(self.history[x]) else []), 
                'score': self.scores[x],
                'name': self.players[x],
                'skipped': x in self.skippedPlayers
                } for x in range(len(self.players))]
        s = sorted(lst, key=itemgetter('score', 'frames', 'started'))
        for i in range(len(s)):
            s[i]['rank'] = i
        return sorted(s, key=itemgetter(sortby))

class DartGame(Component):
    NUMBEROFDARTS = 3

    def __init__(self, players = None, startvalue = 301):
        super(DartGame, self).__init__()
        self.startvalue = startvalue
        self.players = players

    @staticmethod
    def score2sum(score):
        if score.startswith('S'):
            multiplier = 1
        elif score.startswith('D'):
            multiplier = 2
        elif score.startswith('T'):
            multiplier = 3
        else:
            raise Exception("Unknown input: %s" % score)
        score = score[1:]
        return multiplier * int(score)

    def event(self, event):
        self.fire(event)
        #self.flush()        

    def ReceiveInput(self, source, value):
        print ("State is %s, input is %r from %r" % (self.state.state, value, source))
        if source == 'command':
            cmd, param = value.split(' ')
            if cmd == 'skip-player':
                param = int(param)
                skipped = self.state.toggle_skip(param)
                if skipped and self.state.state == 'playing' and self.state.currentPlayer == param and len(self.state.currentDarts) == 0:
                    self.event(SkipPlayer())
                    self.finish_frame(cancel = True)
        if self.state.state == 'hold_in_frame':
            if source == 'code' and value in ['BSTART', 'BGAME']: 
                self.event(LeaveHold(True))
                self.state.next_frame()
                self.start_frame()
        elif self.state.state == 'hold_between_frames':
            if source == 'code' and value in ['BSTART', 'BGAME']  or \
                    source == 'generic' and value == 'next_player': 
                self.event(LeaveHold(False))
                self.state.next_frame()
                self.start_frame()
        elif self.state.state == 'playing': 
            if source == 'generic':
                if value == 'next_player':
                    self.finish_frame(hold = False)
            if source == 'code':
                if value == 'XSTUCK':
                    self.event(DartStuck())
                    print ("Dart is stuck, remove dart!")
                elif value == 'BGAME': #START':
                    self.event(SkipPlayer())
                    self.finish_frame() # hold only if there are darts sticking in the board
                elif value.startswith('X') or value.startswith('B'):
                    self.event(CodeNotImplemented())
                    print ("Not implemented: %s" % value)
                elif value.startswith('S') or value.startswith('D') or value.startswith('T'):
                    print ("* %s hit %s" % (self.state.players[self.state.currentPlayer], value))
                    s = self.score2sum(value)
                    res = self.state.add_dart(value, s)
                    if res == 'bust':
                        self.event(HitBust(self.state, value))
                        print ("** BUST!")
                        self.finish_frame()
                    elif res == 'winner':
                        self.event(HitWinner(self.state, value))
                        print ("** WINNER!")
                        self.finish_frame()
                    else:
                        self.event(Hit(self.state, value))
                        if len(self.state.currentDarts) == self.NUMBEROFDARTS:
                            self.finish_frame()
        elif self.state.state == 'gameover':
            if source != 'serial' or value not in ['BSTART', 'BGAME']:
                return
            

    def finish_frame(self, hold = None, cancel = False):
        self.event(FrameFinished(deepcopy(self.state)))
        if hold == None:
            hold = len(self.state.currentDarts) > 0
        if not cancel:
            self.state.flush_frame()
        else:
            self.state.cancel_frame()
        print ("---- End of frame ---- (winners: %d)" % len(self.state.winners()))
        if len(self.state.winners()) == len(self.state.players) - 1: # all have checked out
            self.event(GameOver(self.state))
            print ("--> Game is over! Ranking:")
            for w in self.state.player_list(sortby='rank'):
                print ("%d: %s" % (w['rank'] + 1, w['name']))
            self.state.state = 'gameover'
        if hold:
            self.event(EnterHold(False))
            self.state.state = 'hold_between_frames'
        else:
            self.state.next_frame()
            self.start_frame()
        
    def started(self, x):
        self.event(StartGame(self.players))

    def StartGame(self, players):
        print ('start game')
        self.players = players
        self.state = GameState(players, self.startvalue)
        self.event(GameInitialized(self.state))
        self.start_frame()

    def start_frame(self):
        print ("--> starting frame")
        self.state.state = 'playing'
        self.event(FrameStarted(self.state))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start a dart game.')
    parser.add_argument('players', metavar='P', type=str, nargs='*',
                        help="player's names")
    parser.add_argument('--snd', default='legacy',
                        help="sound system (none/legacy/espeak)")
    parser.add_argument('--dev', default='/dev/ttyUSB0', 
                        help="input USB device (use none for no USB input)")
    parser.add_argument('--file', help="Read input from this file.")

    parser.add_argument('--debug', action='store_true', help="Enable debug output")
    args = parser.parse_args()

    d = DartGame(args.players) + Webserver
    d += Logger()
    if args.dev != 'none':
        d += DartInput(args.dev)
    if args.file:
        d += FileInput(args.file)
    if args.debug:
        d += Debugger(IgnoreChannels = ['web'])
    if args.snd == 'legacy':
        from components.legacysounds import LegacySounds
        d += LegacySounds()
    elif args.snd == 'espeak':
        from components.espeaksounds import EspeakSounds
        d += EspeakSounds()

    d.run()
    
