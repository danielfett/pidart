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
    SOUND_BASE = '../sounds/old-%s.wav'
    
    SOUNDS = [
        'nextplayer',
        'finish',
        'winner',
        'double',
        'triple',
        'bullseye',
        'beep']

    MUSIC_BASE = '../sounds/wwm/%s.wav'

    MUSIC = [
        'stufe_1_looping',
        'stufe_2',
        'stufe_3'
        ]

    def __init__(self, test=False):
        super(ISATSounds, self).__init__()

        pygame.mixer.pre_init(44100, -16, 2, 1024)
        pygame.init()
        self.music = None
        self.sounds = {}
        volume = 0 if test else 0.9
        for n in self.SOUNDS:
            f = self.SOUND_BASE % n
            if not exists(f):
                raise Exception("File does not exist: %s" % f)
            self.sounds[n] = pygame.mixer.Sound(f)
            self.sounds[n].set_volume(volume)
            
        self.sounds_tts = {}
        for id, sound in texts.items():
            f = isat_filename(id, sound)
            if not exists(f):
                raise Exception("File does not exist: %s" % f)
            self.sounds_tts[id] = pygame.mixer.Sound(f)
            self.sounds_tts[id].set_volume(volume)
        self._say('ready')

    def _play(self, sound):
        while pygame.mixer.get_busy():
            sleep(0.1)
        self.sounds[sound].play() 

    def _say(self, text_id):
        print "Saying %s" % text_id
        while pygame.mixer.get_busy():
            sleep(0.05)
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

    def _adjust_music(self, state):
        if state.state != 'playing':
            if self.music:                
                pygame.mixer.music.fadeout(700)
                self.music = None
            return
        score = state.currentPlayer.score - state.currentScore
        if len(state.currentDarts) == 3 and score > 0:
            # This was the last dart, we don't change the music now.
            return
        
        checkoutable = (score <= 20 or \
             (score <= 60 and score % 3 == 0) or \
             (score <= 40 and score % 2 == 0) or \
             score == 25 or \
             score == 50)

        if score > 180:
            self._play_music(self.MUSIC[0])
        # TODO: move the following check to the tools
        elif checkoutable: 
            # score is single-dart-checkoutable
            self._play_music(self.MUSIC[2])
        else:
            self._play_music(self.MUSIC[1])

        if checkoutable:
            pygame.mixer.music.set_volume(1.0)
        elif score > 180:
            pygame.mixer.music.set_volume(0.4)
        elif score > 60:
            pygame.mixer.music.set_volume(0.6)
        else:
            pygame.mixer.music.set_volume(0.85)

    def _play_music(self, f):
        if self.music == f:
            return
        if self.music:
            pygame.mixer.music.fadeout(700)
        pygame.mixer.music.load(self.MUSIC_BASE % f)
        pygame.mixer.music.play(-1)
        self.music = f

    def _stop_music(self):
        pygame.mixer.music.stop()
        self.music = None

    def DartStuck(self, *args):
        self._play('beep')

    def ManualNextPlayer(self, *args):
        self._play('beep')

    def Hit(self, state, code):
        sleep(0.2)
        self._say_from_rule(hit(state), 'beep')
        self._adjust_music(state)

    def HitBust(self, state, code):
        self._stop_music()
        self._say_from_rule(hit_bust(state), 'winner')
        self._adjust_music(state)

    def HitWinner(self, state, code):
        self._stop_music()
        self._say_from_rule(hit_winner(state), 'finish')
        self._adjust_music(state)

    def GameOver(self, state):
        self._stop_music()

    def EnterHold(self, *args):
        sleep(0.5)
        self._say('press_start')

    def FrameStarted(self, state): 
        self._say('next_player')
        self._adjust_music(state)
