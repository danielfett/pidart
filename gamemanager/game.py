#!/usr/bin/python

players = ['AB', 'CD', 'EF']
from codes import FIELDCODES
from time import sleep
from sys import exit
from circuits import Component, Event, Debugger, Component
from circuits.io.serial import Serial
import serial
import argparse

from components.webserver import Webserver
from components.logger import Logger
from components.legacysounds import LegacySounds
from components.espeaksounds import EspeakSounds

class ReceiveInput(Event):
    """ Some input arrived (fieldcode or other input) """

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

class RoundStarted(Event):
    """ A new round was started. """

class RoundFinished(Event):
    """ A player has thrown three darts (or the round was skipped, etc.) """

class GameOver(Event):
    """ The game is over. """

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



""" MAIN COMPONENT """

from operator import itemgetter

class GameState(object):
    def __init__(self, players, startvalue):
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

    def flush_round(self):
        self.history[self.currentPlayer].append(self.currentDarts)
        self.scores[self.currentPlayer] -= self.currentScore
        self.currentDarts = []
        self.currentScore = 0

    def cancel_round(self):
        self.currentDarts = []
        self.currentScore = 0

    def next_round(self):
        wasPlayer = self.currentPlayer
        winners = self.winners()
        while self.currentPlayer == wasPlayer or self.currentPlayer in winners:
            self.currentPlayer += 1
            if self.currentPlayer == len(self.players):
                self.currentPlayer = 0
                self.round += 1
        
    def winners(self):
        return [x for x in range(len(self.players)) if self.scores[x] == 0]

    def game_over(self):
        return len(self.winners()) == len(self.players) - 1

    def player_list(self, sortby):
        lst = [{
                'started': x, 
                'rounds': len(self.history[x]), 
                'last_round': (self.history[x][-1] if len(self.history[x]) else []), 
                'score': self.scores[x],
                'name': self.players[x]
                } for x in range(len(self.players))]
        s = sorted(lst, key=itemgetter('score', 'rounds', 'started'))
        for i in range(len(s)):
            s[i]['rank'] = i
        if sortby == 'order':
            return sorted(s, key=itemgetter('started'))
        return s

class DartGame(Component):
    NUMBEROFDARTS = 3

    def __init__(self, players, startvalue = 301):
        super(DartGame, self).__init__()
        self.players = players
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
        self.flush()        

    def receive_input(self, input):
        in_type, in_value = input
        if self.state.state == 'hold_in_round':
            if in_type != 'serial' or in_value not in ['BSTART', 'BGAME']:
                return
            self.event(LeaveHold(True))
            self.start_round()
        elif self.state.state == 'hold_between_rounds':
            if in_type != 'serial' or in_value not in ['BSTART', 'BGAME']:
                return
            self.event(LeaveHold(False))
            self.start_round()
        elif self.state.state == 'playing': 
            print "--> Now playing Dart #%d in Round %d: %s (%d Points left)" % (
                len(self.state.currentDarts)+1, 
                self.state.round, 
                self.state.players[self.state.currentPlayer], 
                self.state.scores[self.state.currentPlayer] - self.state.currentScore)
            if in_type == 'serial':
                if in_value == 'XSTUCK':
                    self.event(DartStuck())
                    print "Dart is stuck, remove dart!"
                elif in_value == 'BGAME': #START':
                    self.event(SkipPlayer())
                    self.finish_round(commit = True, hold = len(self.state.currentDarts)) # hold only if there are darts sticking in the board
                elif in_value.startswith('X') or in_value.startswith('B'):
                    self.event(CodeNotImplemented())
                    print "Not implemented: %s" % code
                elif in_value.startswith('S') or in_value.startswith('D') or in_value.startswith('T'):
                    print "Hit %s" % in_value
                    s = self.score2sum(code)
                    res = self.state.add_dart(code, s)
                    if res == 'bust':
                        self.event(HitBust(self.state, code))
                        print "BUST!"
                        self.finish_round(commit = False, hold = True)
                    elif res == 'winner':
                        self.event(HitWinner(self.state, code))
                        print "WINNER!"
                        self.finish_round(commit = True, hold = True)
                    else:
                        self.event(Hit(self.state, code))
                        if len(self.state.currentDarts) == self.NUMBEROFDARTS:
                            self.finish_round(commit = True, hold = True)
        elif self.state.state == 'gameover':
            if in_type != 'serial' or in_value not in ['BSTART', 'BGAME']:
                return
            self.start_game()
            

    def finish_round(self, commit, hold):
        self.event(RoundFinished(self.state))
        if commit:
            self.state.flush_round()
        else:
            self.state.cancel_round()
        if len(self.state.winners()) == len(self.state.players) - 1: # all have checked out
            self.event(GameOver(self.state))
            print "Game is over! Ranking:"
            for w in self.state.player_list(sortby='rank'):
                print "%d: %s" % (w['rank'] + 1, w['name'])
            self.state.state = 'gameover'
        self.state.next_round()
        if hold:
            self.event(EnterHold(False))
            self.state.state = 'hold_between_rounds'
        else:
            self.start_round()
        

    def started(self, *args):
        self.start_game()

    def start_game(self):
        self.state = GameState(self.players, self.startvalue)
        self.event(GameInitialized(self.state))

    def start_round(self):
        self.event(RoundStarted(self.state))
        self.state.state = 'playing'


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start a dart game.')
    parser.add_argument('players', metavar='P', type=str, nargs='+',
                        help="player's names")
    parser.add_argument('--snd', default='legacy',
                        help="sound system (none/legacy/espeak)")
    parser.add_argument('--dev', default='/dev/ttyUSB0',
                        help="input USB device")
    args = parser.parse_args()
    
    d = (DartGame(args.players) + DartInput(args.dev) + Logger() + Debugger())# + Webserver())
    if args.snd == 'legacy':
        d += LegacySounds()
    elif args.snd == 'espeak':
        d += EspeakSounds()
    #d = (DartGame(DartInput(), players) + Logger() + EspeakSounds() + Webserver() + Debugger())
    d.run()
    
