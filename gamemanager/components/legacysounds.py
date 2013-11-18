""" PLAYING SOUNDS """

from circuits import Component
from time import sleep
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
        pygame.mixer.pre_init(44100,-16,2, 1024)
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

    def hit(self, state, code):
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

    def hit_winner(self, state, code):
        self.play('finish')
        print repr(state.winners())
        if len(state.winners()) == 1:
            sleep(3.591)
            self.play('winner')

    def enter_hold(self, manual):
        if manual:
            self.play('beep')

    def leave_hold(self, manual):
        if manual:
            self.play('beep')

    def round_started(self, *args):
        self.play('nextplayer')
