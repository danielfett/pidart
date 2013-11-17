#!/usr/bin/python

players = ['AB', 'CD', 'EF']
from codes import FIELDCODES
from time import sleep
from sys import exit
from circuits import Component, Event, Task, Debugger
import serial

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

class GameInitialized(Task):
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

class WaitForStart(Event):
    """ Wait for the player to hit start. """

class RoundStarted(Event):
    """ A new round was started. """

class RoundFinished(Event):
    """ A player has thrown three darts (or the round was skipped, etc.) """

class GameOver(Event):
    """ The game is over. """

""" LOGGING """

from datetime import datetime

class Logger(Component):
    def game_initialized(self, players):
        print "Logger started."
        filename = datetime.now().strftime("%Y-%m-%d--%H:%M.dartlog")
        self.file = open(filename, 'w')
        self.file.write("Players: %s\n" % (' '.join(players)))

    def round_finished(self, players, currentplayer, darts):
        self.file.write("%s: %s\n" % (players[currentplayer], ' '.join(darts)))

""" PLAYING SOUNDS """

import pygame

class LegacySounds(Component):
    SOUNDS = [
        'nextplayer',
        'finish',
        'winner',
        'double',
        'triple',
        'bullseye',
        'beep']
        

    def __init__(self):
        super(LegacySounds, self).__init__()
        pygame.init()
        self.sounds = {}
        for n in self.SOUNDS:
            self.sounds[n] = pygame.mixer.Sound('../sounds/old-%s.wav' % n)
    
    def play(self, sound):
        self.sounds[sound].play() 

    def dart_stuck(self, *args):
        self.play('beep')

    def skip_player(self, *args):
        self.play('beep')

    def hit(self, players, currentplayer, code):
        if code == 'D25':
            self.play('bullseye')
        elif code.startswith('T'):
            self.play('triple')
        elif code.startswith('D'):
            self.play('double')
        else:
            self.play('beep')

    def hit_bust(self, *args):
        self.play('winner') # sound is missing!

    def hit_winner(self, players, currentplayer, code, winners):
        self.play('finish')
        if len(winners) == 0:
            sleep(3.591)
            self.play('winner')

    def round_started(self, *args):
        self.play('nextplayer')
        
""" Espeak output """

from espeak import espeak

class EspeakSounds(Component):
    def __init__(self):
        super(EspeakSounds, self).__init__()
        espeak.set_voice('en/en-sc')

    def say(self, text):
        espeak.synth("%s!" % text)

    def dart_stuck(self, *args):
        self.say('Dart Stuck.')

    def skip_player(self, *args):
        self.say('Player skipped.')

    def hit(self, players, currentplayer, code):
        sleep(0.25)
        if code == 'S25':
            self.say('Bull\'s eye')
        elif code == 'D25':
            self.say('Inner Bull\'s eye')
        elif code.startswith('T'):
            self.say('Triple %s' % code[1:])
        elif code.startswith('D'):
            self.say('Triple %s' % code[1:])
        else:
            self.say(code[1:])

    def hit_bust(self, *args):
        self.say('Bust')

    def hit_winner(self, players, currentplayer, code, winners):
        if len(winners) == 0:
            self.say('Checked out! You are the winner')
        else:
            self.say('Checked out! You are number %d' % (len(winners) + 1))

    def wait_for_start(self, *args):
        sleep(0.5)
        self.say('Press START')

    def round_started(self, players, currentplayer, round):
        self.say('Next player. Is. %s.' % ('.'.join(players[currentplayer])))

""" Websockets connector """

from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.websocket import WebSocketServerFactory, \
                               WebSocketServerProtocol, \
                               listenWS
 
from threading import Thread
from Queue import Queue
import simplejson

class DartsProtocol(WebSocketServerProtocol):
    def __init__(self):
        self.queue = Queue()

    def onOpen(self):
        self.factory.register(self)     

class DartsServerFactory(WebSocketServerFactory):
   def __init__(self, url, debug = False, debugCodePaths = False):
       WebSocketServerFactory.__init__(self, url, debug = debug, debugCodePaths = debugCodePaths)
       self.clients = []
      
   def broadcast(self, msg):
       for client in self.clients:
           client.sendMessage(simplejson.dumps(msg))
           #client.queue.put(simplejson.dumps(msg))
       

   def register(self, client):
       if not client in self.clients:
           print "registered client " + client.peerstr
           self.clients.append(client)

   def unregister(self, client):
       if client in self.clients:
           print "unregistered client " + client.peerstr
           self.clients.remove(client)

class WSockets(Component):
    def __init__(self):
        super(WSockets, self).__init__()
        self.factory = DartsServerFactory("ws://localhost:9000")

        self.factory.protocol = DartsProtocol
        self.factory.setProtocolOptions(allowHixie76 = True)
        listenWS(self.factory)
        
        webdir = File("../html/")
        web = Site(webdir)
        reactor.listenTCP(8080, web)
        self.thread = Thread(target=reactor.run, args=(), kwargs={'installSignalHandlers':0})
        self.thread.start()

    def hit(self, *args):
        self.factory.broadcast(args)


""" MAIN COMPONENT """

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

    def started(self, *args):
        scores = {}
        history = {}
        for i in range(len(self.players)):
            scores[i] = self.startvalue
            history[i] = []

        currentplayer = 0
        round = 1
        darts = []
        winners = []

        self.event(GameInitialized(self.players))

        while True:
            darts = []
            wait_for_removal_of_darts = True
            self.event(RoundStarted(self.players, currentplayer, round))
            print "=============== Round %d ===============" % round
            while len(darts) < self.NUMBEROFDARTS:
                print "--> Now playing Dart #%d in Round %d: %s (%d Points left)" % (len(darts)+1, round, self.players[currentplayer], scores[currentplayer])
                code = self.input.read()
                if code == 'XSTUCK':
                    self.event(DartStuck())
                    print "Dart is stuck, remove dart!"
                elif code == 'BSTART':
                    self.event(SkipPlayer())
                    print "Player skipped."
                    wait_for_removal_of_darts = False
                    break
                elif code.startswith('X') or code.startswith('B'):
                    self.event(CodeNotImplemented())
                    print "Not implemented: %s" % code
                elif code.startswith('S') or code.startswith('D') or code.startswith('T'):
                    print "Hit %s" % code
                    s = self.score2sum(code)
                    darts.append(code)
                    if scores[currentplayer] - s < 0:
                        self.event(HitBust(self.players, currentplayer, code))
                        print "BUST!"
                        break 
                    elif scores[currentplayer] - s == 0:
                        self.event(HitWinner(self.players, currentplayer, code, winners))
                        print "WINNER!"
                        winners.append(currentplayer)
                        break
                    else:
                        self.event(Hit(self.players, currentplayer, code))
                        scores[currentplayer] -= s

            history[currentplayer].append(darts)
            self.event(RoundFinished(self.players, currentplayer, darts))
            
            if wait_for_removal_of_darts:
                self.event(WaitForStart())
                print "Press start after removing the darts"
                while self.input.read() != 'BSTART':
                    pass

            wasplayer = currentplayer
            while currentplayer == wasplayer or currentplayer in winners:
                currentplayer += 1
                if currentplayer == len(self.players):
                    currentplayer = 0
                    round += 1

            # we have n-1 winners, so the game is over and the current player is last
            if len(winners) == len(self.players) - 1:
                self.event(GameOver(self.players, winners, history))
                print "Game is over! Ranking:"
                for w in winners + [currentplayer]:
                    print "%s (%d)" % (self.players[w], len(history[w]))
                exit()

if __name__ == "__main__":
    #d = DartGame(DartInput(), players)
    #d = (DartGame(DartInput(), players) + Logger() + LegacySounds() + Debugger())
    d = (DartGame(DartInput(), players) + Logger() + EspeakSounds() + WSockets() + Debugger())
    d.run()
    
