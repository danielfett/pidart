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
        self.play('beep')
        self.play('beep')
    
    def play(self, sound):
        self.sounds[sound].play() 

    def DartStuck(self, *args):
        self.play('beep')

    def ManualNextPlayer(self, *args):
        self.play('beep')

    def Hit(self, state, code):
        if code == 'D25':
            self.play('bullseye')
        elif code.startswith('T'):
            self.play('triple')
        elif code.startswith('D'):
            self.play('double')
        else:
            self.play('beep')

    def HitBust(self, *args):
        self.play('winner') # sound is missing!

    def HitWinner(self, state, code):
        self.play('finish')
        sleep(3.591)
        if len(state.winners()) == 1:
            self.play('winner')

    def EnterHold(self, state, manual):
        if manual:
            self.play('beep')

    def LeaveHold(self, state, manual):
        if manual:
            self.play('beep')

    def FrameStarted(self, *args):
        self.play('nextplayer')
