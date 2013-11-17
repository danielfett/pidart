#!/usr/bin/python

players = ['AB', 'CD', 'EF']
from codes import FIELDCODES
from time import sleep
from sys import exit
from circuits import Component, Event, Task, Debugger
import serial
import argparse

from components.webserver import Webserver
from components.logger import Logger
from components.legacysounds import LegacySounds
from components.espeaksounds import EspeakSounds

class DartInput(object):
    def __init__(self, device = '/dev/ttyUSB0'):
        self.ser = serial.Serial(device, 115200)
        sleep(1) # for arduino's reset circuit
        
    def read(self):
        inp = ord(self.ser.read(1))
        try:
            return FIELDCODES[inp]
        except KeyError:
            raise Exception("Unknown fieldcode: %x" % inp)

class FakeInput(object):
    def read(self):
        inp = raw_input("? ").strip().upper()
        return inp

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

    def add_dart(self, dart, s):
        self.currentDarts.append(dart)
        if self.scores[self.currentPlayer] - s < 0:
            return 'bust'
        self.scores[self.currentPlayer] -= s
        if self.scores[self.currentPlayer] == 0:
            return 'winner'

    def flush_round(self):
        self.history[self.currentPlayer].append(self.currentDarts)
        self.currentDarts = []

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

    def __init__(self, inp, players, startvalue = 301):
        super(DartGame, self).__init__()
        self.input = inp
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

    def hold(self, manual):
        self.event(EnterHold(manual))
        print "Press game or start after removing the darts"
        while self.input.read() not in ['BSTART', 'BGAME']:
            pass
        self.event(LeaveHold(manual))

    def started(self, *args):
        state = GameState(self.players, self.startvalue)

        self.event(GameInitialized(state))

        while True:
            wait_for_removal_of_darts = True
            self.event(RoundStarted(state))
            print "=============== Round %d ===============" % state.round
            while len(state.currentDarts) < self.NUMBEROFDARTS:
                print "--> Now playing Dart #%d in Round %d: %s (%d Points left)" % (
                    len(state.currentDarts)+1, 
                    state.round, 
                    state.players[state.currentPlayer], 
                    state.scores[state.currentPlayer])
                code = self.input.read()
                if code == 'XSTUCK':
                    self.event(DartStuck())
                    print "Dart is stuck, remove dart!"
                elif code == 'BSTART':
                    self.event(SkipPlayer())
                    print "Player skipped."
                    wait_for_removal_of_darts = False
                    break
                elif code == 'BGAME':
                    self.hold(True)
                elif code.startswith('X') or code.startswith('B'):
                    self.event(CodeNotImplemented())
                    print "Not implemented: %s" % code
                elif code.startswith('S') or code.startswith('D') or code.startswith('T'):
                    print "Hit %s" % code
                    s = self.score2sum(code)
                    res = state.add_dart(code, s)
                    if res == 'bust':
                        self.event(HitBust(state, code))
                        print "BUST!"
                        break 
                    elif res == 'winner':
                        self.event(HitWinner(state, code))
                        print "WINNER!"
                        break
                    else:
                        self.event(Hit(state, code))

            self.event(RoundFinished(state))
            state.flush_round()
            
            if wait_for_removal_of_darts:
                self.hold(False)

            # we have n-1 winners, so the game is over and the current player is last
            if state.game_over():
                self.event(GameOver(state))
                print "Game is over! Ranking:"
                for w in state.player_list(sortby='rank'):
                    print "%d: %s" % (w['rank'] + 1, w['name'])
                exit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start a dart game.')
    parser.add_argument('players', metavar='P', type=str, nargs='+',
                        help="player's names")
    parser.add_argument('--snd', default='legacy',
                        help="sound system (none/legacy/espeak)")
    args = parser.parse_args()
    
    d = (DartGame(DartInput(), args.players) + Logger() + Webserver() + Debugger())
    if args.snd == 'legacy':
        d += LegacySounds()
    elif args.snd == 'espeak':
        d += EspeakSounds()
    #d = (DartGame(DartInput(), players) + Logger() + EspeakSounds() + Webserver() + Debugger())
    d.run()
    
