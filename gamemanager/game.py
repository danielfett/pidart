#!/usr/bin/python

from codes import FIELDCODES
from time import sleep
from sys import exit
from circuits import Component, Event, Debugger, Component
from circuits.io.serial import Serial
from circuits.io.file import File
import serial
import argparse

from components.webserver import Webserver
from components.logger import Logger
from components.legacysounds import LegacySounds
from components.espeaksounds import EspeakSounds

class ReceiveInput(Event):
    """ Some input arrived (fieldcode or other input) """

class StartGame(Event):
    """ Start a new game. """

class GameInitialized(Event):
    """ A new game was started. """

class DartStuck(Event):
    """ A dart is stuck. May be fired many times in a row. """

class SkipPlayer(Event):
    """ The button for skipping a player was pressed. """

class CodeNotImplemented(Event):
    """ This part of the code is not implemented. """

class Hit(Event):
    """ A dart hit the board. """

class HitBust(Event):
    """ A dart hit the board, but busted. """

class HitWinner(Event):
    """ A dart hit the board, and the player won. """

class EnterHold(Event):
    """ Wait for the player to hit start. """

class LeaveHold(Event):
    """ Player has pressed start to continue. """

class FrameStarted(Event):
    """ A new frame was started. """

class FrameFinished(Event):
    """ A player has thrown three darts (or the round was skipped, etc.) """

class GameOver(Event):
    """ The game is over. """

'''
class DartInput(Component):
    def __init__(self, device = '/dev/ttyUSB0'):
        super(DartInput, self).__init__()
        #self.ser = serial.Serial(device, 115200)
        #sleep(1) # for arduino's reset circuit
        Serial(device, baudrate = 115200, bufsize = 1, timeout = 0, channel = 'serial').register(self)
        sleep(1)
        
    def do_read(self, data):
        print data
        for b in data:
            try:
                self.fire(ReceiveInput(('serial', FIELDCODES[b])))
            except KeyError:
                raise Exception("Unknown fieldcode: %x" % inp)

    def generate_events(self, event):
        

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

    def game_initialized(self, state):
        for s in self.data[1:]:
            if s.startswith('('): # this is a comment, so ignore.
                pass
            elif s == '|': # next player
                self.fire(ReceiveInput(('generic', 'next_player')))
            else:
                self.fire(ReceiveInput(('code', s)))


""" MAIN COMPONENT """

from operator import itemgetter

class GameState(object):
    def __init__(self, players, startvalue):
        self.state = None
        self.players = players
        self.scores = {}
        self.history = {}
        self.round = 1

        for i in range(len(self.players)):
            self.scores[i] = startvalue
            self.history[i] = []

        self.currentPlayer = 0
        self.currentDarts = []
        self.currentScore = 0

    def add_dart(self, dart, s):
        self.currentDarts.append(dart)
        self.currentScore += s
        if self.scores[self.currentPlayer] - self.currentScore < 0:
            return 'bust'
        if self.scores[self.currentPlayer] - self.currentScore ==  0:
            return 'winner'

    def flush_frame(self):
        self.history[self.currentPlayer].append(self.currentDarts)
        result = self.scores[self.currentPlayer] - self.currentScore
        if result >= 0:
            self.scores[self.currentPlayer] = result
        self.currentDarts = []
        self.currentScore = 0

    def next_frame(self):
        wasPlayer = self.currentPlayer
        winners = self.winners()
        while self.currentPlayer == wasPlayer or self.currentPlayer in winners:
            self.currentPlayer += 1
            if self.currentPlayer == len(self.players):
                self.currentPlayer = 0
                self.round += 1
                print "==== End of Round. ===="
                print "#Frames\tPlayer\tScore\tRank"
                for p in self.player_list(sortby = 'started'):
                    print "%(frames)d\t%(name)s\t%(score)d\t%(rank)d" % p
        
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
                'name': self.players[x]
                } for x in range(len(self.players))]
        s = sorted(lst, key=itemgetter('score', 'frames', 'started'))
        for i in range(len(s)):
            s[i]['rank'] = i
        return sorted(s, key=itemgetter(sortby))

class DartGame(Component):
    NUMBEROFDARTS = 3

    def __init__(self, startvalue = 301):
        super(DartGame, self).__init__()
        self.startvalue = startvalue

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

    def receive_input(self, input):
        print "State is %s, input is %r" % (self.state.state, input)
        in_type, in_value = input
        if self.state.state == 'hold_in_frame':
            if in_type == 'code' and in_value in ['BSTART', 'BGAME']: 
                self.event(LeaveHold(True))
                self.start_frame()
        elif self.state.state == 'hold_between_frames':
            if in_type == 'code' and in_value in ['BSTART', 'BGAME']  or \
                    in_type == 'generic' and in_value == 'next_player': 
                self.event(LeaveHold(False))
                self.start_frame()
        elif self.state.state == 'playing': 
            '''            print "[%s] --> dart #%d in Round %d (%d Points left)" % (
                self.state.players[self.state.currentPlayer], 
                len(self.state.currentDarts)+1, 
                self.state.round, 
                self.state.scores[self.state.currentPlayer] - self.state.currentScore)'''
            if in_type == 'generic':
                if in_value == 'next_player':
                    self.finish_frame(hold = False)
            if in_type == 'code':
                if in_value == 'XSTUCK':
                    self.event(DartStuck())
                    print "Dart is stuck, remove dart!"
                elif in_value == 'BGAME': #START':
                    self.event(SkipPlayer())
                    self.finish_frame() # hold only if there are darts sticking in the board
                elif in_value.startswith('X') or in_value.startswith('B'):
                    self.event(CodeNotImplemented())
                    print "Not implemented: %s" % in_value
                elif in_value.startswith('S') or in_value.startswith('D') or in_value.startswith('T'):
                    print "* %s hit %s" % (self.state.players[self.state.currentPlayer], in_value)
                    s = self.score2sum(in_value)
                    res = self.state.add_dart(in_value, s)
                    if res == 'bust':
                        self.event(HitBust(self.state, in_value))
                        print "** BUST!"
                        self.finish_frame()
                    elif res == 'winner':
                        self.event(HitWinner(self.state, in_value))
                        print "** WINNER!"
                        self.finish_frame()
                    else:
                        self.event(Hit(self.state, in_value))
                        if len(self.state.currentDarts) == self.NUMBEROFDARTS:
                            self.finish_frame()
        elif self.state.state == 'gameover':
            if in_type != 'serial' or in_value not in ['BSTART', 'BGAME']:
                return
            

    def finish_frame(self, hold = None):
        self.event(FrameFinished(self.state))
        if hold == None:
            hold = len(self.state.currentDarts) > 0
        self.state.flush_frame()
        print "---- End of frame ---- (winners: %d)" % len(self.state.winners())
        if len(self.state.winners()) == len(self.state.players) - 1: # all have checked out
            self.event(GameOver(self.state))
            print "--> Game is over! Ranking:"
            for w in self.state.player_list(sortby='rank'):
                print "%d: %s" % (w['rank'] + 1, w['name'])
            self.state.state = 'gameover'
        self.state.next_frame()
        if hold:
            self.event(EnterHold(False))
            self.state.state = 'hold_between_frames'
        else:
            self.start_frame()
        

    def start_game(self, players):
        self.players = players
        self.state = GameState(players, self.startvalue)
        self.event(GameInitialized(self.state))
        self.start_frame()

    def start_frame(self):
        print "--> starting frame"
        self.state.state = 'playing'
        self.event(FrameStarted(self.state))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start a dart game.')
    parser.add_argument('players', metavar='P', type=str, nargs='*',
                        help="player's names")
    parser.add_argument('--snd', default='legacy',
                        help="sound system (none/legacy/espeak)")
    parser.add_argument('--dev', default='/dev/ttyUSB0',
                        help="input USB device")
    parser.add_argument('--file', help="Read input from this file.")

    parser.add_argument('--debug', type=bool, help="Enable debug output")
    args = parser.parse_args()

    d = (DartGame() + Logger())# + Webserver())
    if args.file:
        d += FileInput(args.file)
    if args.debug:
        d += Debugger()

    '''
    d = (DartGame(args.players) + DartInput(args.dev) + Logger() + Debugger())# + Webserver())
    if args.snd == 'legacy':
        d += LegacySounds()
    elif args.snd == 'espeak':
        d += EspeakSounds()
    '''
    d.run()
    d.fire(StartGame(args.players))
    
