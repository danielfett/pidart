#!/usr/bin/python

from time import sleep
from datetime import datetime
from platform import node
from sys import exit, executable, argv
from os import execl
from operator import methodcaller, itemgetter
from copy import deepcopy
import argparse

from circuits import Component, Event, Debugger, handler

from events import *
from components.webserver import DartsWebServer
from components.logger import Logger, DetailedLogger
from components.input import DartInput, FileInput
from components.isatsounds import ISATSounds
from components.espeaksounds import EspeakSounds
from components.legacysounds import LegacySounds

reload_afterwards = False # this is set to true to reload this python file after execution

""" MAIN COMPONENT """

def score2sum(score):
    if score.startswith('S'):
        multiplier = 1
    elif score.startswith('D'):
        multiplier = 2
    elif score.startswith('T'):
        multiplier = 3
    else:
        raise Exception("Unknown input: %s" % score)
    if score.endswith('i'):
        score = score[:-1]
    score = score[1:]
    return multiplier * int(score)

class Player(object):
    OKAY = 'ok'
    CHECKOUT = 'checkout'
    BUST = 'bust'

    def __init__(self, name, index, startvalue):
        self.index = index
        self.name = name
        self.history = []
        self.startvalue = startvalue
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
        before = score
        text = self.check_score(score)
        if text == self.OKAY:
            self.score -= score
            text = "%d" % score
        elif text == self.CHECKOUT:
            self.score -= score
        self.history.append({'before': before, 'text': text, 'darts': darts})

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

    def change_history(self, frame, oldDarts, newDarts):
        if self.history[frame]['darts'] != oldDarts:
            raise ValueError("Cannot change last round. Expected oldDarts: %r, actual oldDarts: %r." % (
                    oldDarts,
                    self.history[frame]
                ))

        self.history[frame]['darts'] = newDarts
        self._recalculate_score()

    def undo_last_frame(self):
        if len(self.history) > 0:
            self.history.pop()
        self._recalculate_score()            

    def _recalculate_score(self):
        self.score = self.startvalue
        history = self.history
        self.history = []
        for h in history:
            darts = h['darts']
            darts_sum = sum(map(score2sum, darts))
            print "Recalculating... %r (=%d)" % (darts, darts_sum)
            self.add_score(darts, darts_sum)  

class GameState(object):
    def __init__(self, players, startvalue, gameid, testgame):
        self.state = None
        self.players = []
        self.startvalue = startvalue
        for i in range(len(players)):
            self.players.append(Player(players[i], i, startvalue))

        if len(self.players):
            self.nextPlayer = self.players[0]
        self.currentDarts = []
        self.previousScore = self.currentScore = 0
        self._update_ranks()
        self.id = gameid
        self.testgame = testgame
        self.history = []

    def add_dart(self, dart, s):
        self.currentDarts.append(dart)
        self.previousScore = self.currentScore
        self.currentScore += s
        return self.currentPlayer.check_score(self.currentScore)

    def flush_frame(self):
        self.currentPlayer.add_score(self.currentDarts, self.currentScore)
        self.currentDarts = []
        self.currentScore = 0
        self.previousScore = 0
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
            diff = 0 if (last_man_standing.index < worst_checkout.index) else 1
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

    ''' This is idempotent. Repeat it whenever you want. '''
    def prepare_next_player(self):
        self.nextPlayer = self._get_next_player()
        return self.nextPlayer

    def advance_player(self):
        self.currentPlayer = self.nextPlayer
        self.nextPlayer = None

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

    def change_player_history(self, player, frame, oldDarts, newDarts):
        self.players[player].change_history(frame, oldDarts, newDarts)
        self._update_ranks()

    def undo_last_frame(self, player):
        self.players[player].undo_last_frame()
        self._update_ranks()

    """
    Gets a list of names of players and changes the list of players in
    the current game accordingly by adding or removing players if
    needed. Returns true if the current player has left the game.

    """
    def update_players(self, players):
        newPlayers = []
        for name in players:
            for existing in self.players:
                if existing.name == name:
                    existing.index = len(newPlayers)
                    newPlayers.append(existing)
                    break
            else:
                newPlayers.append(Player(name, len(newPlayers), self.startvalue))
        self.players = newPlayers
        self._update_ranks()

        return self.currentPlayer not in newPlayers
            
class DartGame(Component):
    NUMBEROFDARTS = 3
    
    def __init__(self, one_game = False):
        Component.__init__(self)
        self.state = GameState([], 0, None, True)
        self.one_game = one_game
        
    def StartGame(self, players, startvalue, testgame):
        # generate a more or less unique id for this game
        date = datetime.now().strftime("%Y-%m-%d--%H:%M:%S")
        gameid = "%s--%s" % (node(), date)
        self.state = GameState(players, startvalue, gameid, testgame)
        self.fire(GameInitialized(self.state))
        self.start_frame()

    def start_frame(self):
        print ("--> starting frame")
        self.state.state = 'playing'
        self.state.advance_player()
        self.fire(FrameStarted(self.state))

    def SkipPlayer(self, player):
        skipped = self.state.toggle_skip(self.state.players[player])
        if skipped:
            if self.state.state == 'playing' and self.state.currentPlayer.index == player and len(self.state.currentDarts) == 0:
                self.finish_frame(hold=False, cancel=True)                
            # we can safely repeat the preparation for the next
            # player here, as it is idempotent. It cannot output
            # None (for gameover) here, as then it would have done
            # so already earlier.                
            if self.state.prepare_next_player() == None:
                self.gameover()
                
    def UndoLastFrame(self, player):
        self.state.undo_last_frame(player)
        if self.state.prepare_next_player() == None:
            self.gameover()
            return
        self.fire(GameStateChanged(self.state))
               
    def ChangeLastRound(self, player, oldDarts, newDarts):
        try:
            self.state.change_player_history(player, -1, oldDarts, newDarts)
            if self.state.prepare_next_player() == None:
                self.gameover()
                return
            elif self.state.state == 'gameover':
                self.start_frame()
            self.fire(GameStateChanged(self.state))
        except ValueError, e:
            print e

    def UpdatePlayers(self, players):
        if self.state.update_players(players) and \
           self.state.state == 'playing':
            self.finish_frame(hold=False, cancel=True)   
        else:
            self.fire(GameStateChanged(self.state))
        

    def ReceiveInput(self, source, value):
        print ("State is %s, input is %r from %r" % (self.state.state, value, source))
        if self.state.state == 'hold':
            if source == 'code' and value in ['BSTART', 'BGAME']  or \
                    source == 'generic' and value == 'next_player': 
                self.fire(LeaveHold(self.state, False))
                self.start_frame()
        elif self.state.state == 'playing': 
            if source == 'generic':
                if value == 'next_player':
                    self.finish_frame(hold=False)
                elif value == 'cancel_game':
                    self.state.state = 'gameover'
                    self.fire(GameOver(deepcopy(self.state)))
            if source == 'code':
                if value == 'XSTUCK':
                    self.fire(DartStuck())
                    print ("Dart is stuck, remove dart!")
                elif value == 'BGAME': #START':
                    self.fire(ManualNextPlayer())
                     # hold only if there are darts sticking in the board
                    self.finish_frame(hold=len(self.state.currentDarts) > 0)
                elif value.startswith('X') or value.startswith('B'):
                    self.fire(CodeNotImplemented())
                    print ("Not implemented: %s" % value)
                elif value.startswith('S') or value.startswith('D') or value.startswith('T'):
                    print ("* %s hit %s" % (self.state.currentPlayer.name, value))
                    s = score2sum(value)
                    res = self.state.add_dart(value, s)
                    if res == Player.BUST:
                        self.fire(HitBust(deepcopy(self.state), value))
                        print ("** BUST!")
                        self.finish_frame(hold=True)
                    elif res == Player.CHECKOUT:
                        self.fire(HitWinner(deepcopy(self.state), value))
                        print ("** WINNER!")
                        self.finish_frame(hold=True)
                    else:
                        self.fire(Hit(deepcopy(self.state), value))
                        if len(self.state.currentDarts) == self.NUMBEROFDARTS:
                            self.finish_frame(hold=True)
        elif self.state.state == 'gameover':
            # todo
            pass
            

    def finish_frame(self, hold=False, cancel=False):
        self.fire(FrameFinished(deepcopy(self.state)))
        if not cancel:
            self.state.flush_frame()
        if self.state.prepare_next_player() == None:
            self.gameover()
        elif hold:
            self.state.state = 'hold'
            self.fire(EnterHold(self.state, False))
        else:
            self.start_frame()

    def gameover(self):
        self.state.state = 'gameover'
        self.fire(GameOver(deepcopy(self.state)))
        print ("--> Game is over! Ranking:")
        for w in self.state.player_list(sortby='rank'):
            print ("%d: %s" % (w['rank'] + 1, w['name']))
        if self.one_game:
            self.root.stop()


class DartManager(Component):

    SOUND_COMPONENTS = {
        'none': type(None),
        'isat': ISATSounds,
        'espeak': EspeakSounds,
        'legacy': LegacySounds
    }
    def __init__(self, one_game):
        Component.__init__(self)
        
        VersionManager().register(self)
        DartGame(one_game).register(self)
        DartsWebServer().register(self)
        Logger().register(self)
        DetailedLogger().register(self)
        
        self.inputsys = None
        self.soundsys = type(None)
        self.logsys = None

    def set_sound(self, newsnd):
        newtype = self.SOUND_COMPONENTS[newsnd]
        if self.soundsys != type(None) and type(self.soundsys) != newtype:
            print "unregistering old soundsys"
            self.soundsys.unregister()

        if newtype == type(None):
            self.soundsys = None
        else:
            self.soundsys = newtype()
            self.soundsys.register(self)
        self.fireEvent(SettingsChanged({'sound': newsnd}))
    
    # TODO: the serial device is not closed properly
    def set_input_device(self, path):
        if self.inputsys:
            self.inputsys.unregister()
            self.inputsys = None
        if path:
            self.inputsys = DartInput(path)
            self.inputsys.register(self)
            self.fireEvent(SettingsChanged({'inputDevice': path}))

    '''
    File input unregisters itself once it has finished.
    '''
    def set_input_file(self, path):
        if path:
            fi = FileInput(path)
            fi.register(self)
    
    @handler('UpdateSettings')
    def handle_set_config(self, config):
        if 'sound' in config:
            self.set_sound(config['sound'])
        if 'inputDevice' in config:
            self.set_input_device(config['inputDevice'])
        if 'inputFile' in config:
            self.set_input_file(config['inputFile'])

class VersionManager(Component):

    @handler('PerformSelfUpdate')
    def self_update(self):
        global reload_afterwards
        print "Self-updating..."
        from subprocess import Popen
        p = Popen("git pull", shell=True)
        (stdoutdata, stderrdata) = p.communicate()
        if p.returncode != 0:
            self.fire(ErrorMessage("Unable to execute git pull; error:\n%s" % stderrdata))
            return 
        print "Stopping..."
        reload_afterwards = True
        self.root.stop()
        


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start a dart game.')
    parser.add_argument('players', metavar='P', type=str, nargs='*',
                        help="player's names")
    parser.add_argument('--init', default=301, type=int, 
                        help="initial number of points")
    parser.add_argument('--snd', default='isat',
                        help="sound system (none/isat/legacy/espeak)")
    parser.add_argument('--dev', default='', 
                        help="input USB device (use empty string for no serial input)")
    parser.add_argument('--file', help="Read input from this file.", default='')
    parser.add_argument('--debug', action='store_true', help="Enable debug output")
    parser.add_argument('--nolog', action='store_true', help="Disable single-dart logging")
    parser.add_argument('--test', action='store_true', help="This is a test game, do no permanent changes.")
    parser.add_argument('--one-game', action='store_true', help="Play only one game and then finish.")
    args = parser.parse_args()

    m = DartManager(args.one_game)

    settings = {
        'sound': args.snd,
        'inputDevice': args.dev,
        'inputFile': args.file,
        'logging': True
    }
    if args.debug:
        m += Debugger(IgnoreChannels = ['web'])
    
    m.fire(UpdateSettings(settings))

    if len(args.players):
        m.fire(StartGame(args.players, args.init, args.test))
    m.run()
    if reload_afterwards:
        print "Reloading..."
        execl(executable, *([executable]+argv))
