"""
Output different sound files depending on the game situation.
"""

from circuits import Component
from time import sleep
import pygame
from random import randint
from os.path import exists

from isat.tools import isat_filename
from isat.rules import texts, hit, hit_bust, hit_winner

class ISATSounds(Component):
    SOUNDS = [
        'nextplayer',
        'finish',
        'winner',
        'double',
        'triple',
        'bullseye',
        'beep']

    def __init__(self, silent = False):
        super(ISATSounds, self).__init__()

        pygame.mixer.pre_init(44100, -16, 2, 1024)
        pygame.init()
        self.sounds = {}
        for n in self.SOUNDS:
            f = '../sounds/old-%s.wav' % n
            if not exists(f):
                raise Exception("File does not exist: %s" % f)
            self.sounds[n] = pygame.mixer.Sound(f)
        if silent:
            for n in self.SOUNDS:
                self.sounds[n].set_volume(0)
            
        self.sounds_tts = {}
        for id, sound in texts.items():
            f = isat_filename(id, sound)
            if not exists(f):
                raise Exception("File does not exist: %s" % f)
            self.sounds_tts[id] = pygame.mixer.Sound(f)
        if silent:
            for id, _ in texts.items():
                self.sounds_tts[id].set_volume(0)
        self._say('ready')

    def _play(self, sound):
        while pygame.mixer.get_busy():
            sleep(0.1)
        self.sounds[sound].play() 

    def _say(self, text_id):
        print "Saying %s" % text_id
        while pygame.mixer.get_busy():
            sleep(0.1)
        self.sounds_tts[text_id].play()

    def _say_from_rule(self, rules, alt):
        try:
            weights_sum = sum([x['weight'] for x in rules if x['use']])
            rnd = randint(0, weights_sum)
            for rule in rules:
                if not rule['use']:
                    continue
                rnd -= rule['weight']
                if rnd <= 0:
                    self._say(rule['text'])
                    return
        except Exception, e:
            print e
            self._play(alt)
            

    def DartStuck(self, *args):
        self._play('beep')

    def ManualNextPlayer(self, *args):
        self._play('beep')

    def Hit(self, state, code):
        sleep(0.25)
        self._say_from_rule(hit(state), 'beep')

    def HitBust(self, state, code):
        self._say_from_rule(hit_bust(state), 'winner')

    def HitWinner(self, state, code):
        self._say_from_rule(hit_winner(state), 'finish')

    def EnterHold(self, *args):
        sleep(0.5)
        self._say('press_start')

    def FrameStarted(self, state): 
        self._say('next_player')
