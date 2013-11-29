""" Espeak output """

from circuits import Component
from time import sleep
from namemapping import name_mapping
import pygame

from text_list import text_dir, texts

class InfSecSounds(Component):
    STATIC_SOUNDS = [
        'nextplayer',
        'finish',
        'winner',
        'double',
        'triple',
        'bullseye',
        'beep']

    def __init__(self):
        super(EspeakSounds, self).__init__()

        # Initialize espeak
        espeak.set_voice('en/en-sc')
        pygame.mixer.pre_init(44100,-16,2, 1024)

        # ...and pygame
        pygame.init()
        self.sounds = {}
        for n in self.SOUNDS:
            self.sounds[n] = pygame.mixer.Sound('../sounds/old-%s.wav' % n)

    def play(self, sound):
        self.sounds[sound].play() 

    def say(self, text):
        espeak.synth("%s!" % text)

    def DartStuck(self, *args):
        self.say('Dart Stuck.')

    def ManualNextPlayer(self, *args):
        self.say('Hold.')

    def Hit(self, state, code):
        sleep(0.25)
        if code == 'S25':
            self.say('Bull\'s eye')
        elif code == 'D25':
            self.say('Inner Bull\'s eye')
        elif code.startswith('D'):
            self.say('Double %s' % code[1:])
        elif code.startswith('T'):
            self.say('Triple %s' % code[1:])
        else:
            self.say(code[1:])

    def HitBust(self, *args):
        self.say('Bust')

    def HitWinner(self, state, code):
        if len(state.winners()) == 1:
            self.say('Checked out! You are the winner')
        else:
            self.say('Checked out! You are number %d' % (len(state.winners())))

    def EnterHold(self, *args):
        sleep(0.5)
        self.say('Press START')

    def FrameStarted(self, state):
        name = name_mapping.get(state.currentPlayer.name, '.'.join(state.currentPlayer.name))
        self.say('Next player. Is. %s.' % (name))

    def GameOver(self, *args):
        self.say('Game over')
