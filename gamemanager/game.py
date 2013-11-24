#!/usr/bin/python

from time import sleep
from sys import exit
from operator import methodcaller, itemgetter
from copy import deepcopy
import argparse

from circuits import Component, Event, Debugger, handler

from events import *
from components.webserver import Webserver
from components.logger import Logger
from components.input import DartInput, FileInput

""" MAIN COMPONENT """

class Player(object):
    OKAY = 'ok'
    CHECKOUT = 'checkout'
    BUST = 'bust'

    def __init__(self, name, index, startvalue):
        self.index = index
        self.name = name
        self.history = []
        self.score = startvalue
        self.skipped = False
        self.rank = 0

    def check_score(self, score):
        a = self.score - score
        if a > 0:
            return self.OKAY
        elif a == 0:
            return self.CHECKOUT
        else:
            return self.BUST

    def add_score(self, darts, score):
        text = self.check_score(score)
        if text == self.OKAY:
            self.score -= score
            text = "%d" % score
        elif text == self.CHECKOUT:
            self.score -= score
        self.history.append({'text': text, 'darts': darts})

    def toggle_skip(self):
        self.skipped = not self.skipped
        return self.skipped

    def get_info(self):
        return {
            'started': self.index, 
            'frames': len(self.history), 
            'last_frame': (self.history[-1] if len(self.history) else []), 
            'score': self.score,
            'name': self.name,
            'skipped': self.skipped,
            'rank': self.rank
            }

    def set_rank(self, r):
        self.rank = r
        

class GameState(object):
    def __init__(self, players, startvalue):
        self.state = None
        self.players = []
        for i in range(len(players)):
            self.players.append(Player(players[i], i, startvalue))

        self.nextPlayer = self.players[0] # fails if zero players
        self.currentDarts = []
        self.currentScore = 0
        self._update_ranks()

    def add_dart(self, dart, s):
        self.currentDarts.append(dart)
        self.currentScore += s
        return self.currentPlayer.check_score(self.currentScore)

    def flush_frame(self):
        self.currentPlayer.add_score(self.currentDarts, self.currentScore)
        self.currentDarts = []
        self.currentScore = 0
        self._update_ranks()

    def _get_next_player(self):
        lst_playing = [p for p in self.players if p.score > 0]
        if len(lst_playing) == 0:
            return None
        elif len(lst_playing) == 1:
            last_man_standing = lst_playing[0]

            # now find the worst player that checked out
            lst_checked_out = [p for p in self.players if p.score == 0]
            if len(lst_checked_out) == 0:
                return last_man_standing
            lst_worst_checkout = sorted(lst_checked_out, key=lambda p: len(p.history))
            worst_checkout = lst_worst_checkout[-1]
            
            # let our current player play only if there is a chance to
            # be not the last

            # how many rounds (at least) must be between the last man
            # standing and the worst checkout player?
            diff = 0 if (worst_checkout.index < last_man_standing.index) else 1
            if len(last_man_standing.history) < len(worst_checkout.history) - diff:
                return last_man_standing 
            else:
                return None
        # else...
        lst_next_player = sorted(lst_playing, key=lambda p: (p.skipped, len(p.history), p.index))
        nextPlayer = lst_next_player[0]
        if nextPlayer.skipped:
            nextPlayer.toggle_skip()
        return nextPlayer

    def prepare_next_player(self):
        self.nextPlayer = self._get_next_player()
        return self.nextPlayer

    def advance_player(self):
        self.currentPlayer = self.nextPlayer

    def toggle_skip(self, player):
        return self.players[player.index].toggle_skip()
        
    def winners(self):
        return [p for p in self.players if p.score == 0]

    def _update_ranks(self):
        s = sorted(self.players, key=lambda p: (p.score, len(p.history), p.index))
        for i in range(len(s)):
            s[i].set_rank(i)

    def player_list(self, sortby = 'started'):
        lst = [p.get_info() for p in self.players]
        return sorted(lst, key=itemgetter(sortby))

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

    def SkipPlayer(self, player):
        skipped = self.state.toggle_skip(self.state.players[player])
        if skipped and self.state.state == 'playing' and self.state.currentPlayer.index == player and len(self.state.currentDarts) == 0:
            self.finish_frame(cancel = True)

    def ReceiveInput(self, source, value):
        print ("State is %s, input is %r from %r" % (self.state.state, value, source))
        if self.state.state == 'hold_in_frame':
            if source == 'code' and value in ['BSTART', 'BGAME']: 
                self.event(LeaveHold(True))
                self.start_frame()
        elif self.state.state == 'hold_between_frames':
            if source == 'code' and value in ['BSTART', 'BGAME']  or \
                    source == 'generic' and value == 'next_player': 
                self.event(LeaveHold(False))
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
                    self.event(ManualNextPlayer())
                    self.finish_frame() # hold only if there are darts sticking in the board
                elif value.startswith('X') or value.startswith('B'):
                    self.event(CodeNotImplemented())
                    print ("Not implemented: %s" % value)
                elif value.startswith('S') or value.startswith('D') or value.startswith('T'):
                    print ("* %s hit %s" % (self.state.currentPlayer.name, value))
                    s = self.score2sum(value)
                    res = self.state.add_dart(value, s)
                    if res == Player.BUST:
                        self.event(HitBust(self.state, value))
                        print ("** BUST!")
                        self.finish_frame()
                    elif res == Player.CHECKOUT:
                        self.event(HitWinner(self.state, value))
                        print ("** WINNER!")
                        self.finish_frame()
                    else:
                        self.event(Hit(self.state, value))
                        if len(self.state.currentDarts) == self.NUMBEROFDARTS:
                            self.finish_frame()
        elif self.state.state == 'gameover':
            # todo
            pass
            

    def finish_frame(self, hold = None, cancel = False):
        self.event(FrameFinished(self.state))
        if not cancel:
            self.state.flush_frame()
        if self.state.prepare_next_player() == None:
            self.gameover()
        elif hold or (hold == None and len(self.state.currentDarts) > 0):
            self.event(EnterHold(False))
            self.state.state = 'hold_between_frames'
        else:
            self.start_frame()

    def gameover(self):
        self.state.state = 'gameover'
        self.event(GameOver(self.state))
        print ("--> Game is over! Ranking:")
        for w in self.state.player_list(sortby='rank'):
            print ("%d: %s" % (w['rank'] + 1, w['name']))
        
    def started(self, x):
        self.event(StartGame(self.players))

    def StartGame(self, players):
        self.players = players
        self.state = GameState(players, self.startvalue)
        self.event(GameInitialized(self.state))
        self.start_frame()

    def start_frame(self):
        print ("--> starting frame")
        self.state.state = 'playing'
        self.state.advance_player()
        self.event(FrameStarted(self.state))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start a dart game.')
    parser.add_argument('players', metavar='P', type=str, nargs='*',
                        help="player's names")

    parser.add_argument('--init', default=301, type=int, 
                        help="initial number of points")
    parser.add_argument('--snd', default='legacy',
                        help="sound system (none/legacy/espeak)")
    parser.add_argument('--dev', default='/dev/ttyUSB0', 
                        help="input USB device (use none for no USB input)")
    parser.add_argument('--file', help="Read input from this file.")

    parser.add_argument('--debug', action='store_true', help="Enable debug output")
    args = parser.parse_args()

    d = DartGame(args.players, args.init) + Webserver
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
    
