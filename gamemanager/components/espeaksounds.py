""" Espeak output """

from espeak import espeak
from circuits import Component
from time import sleep

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

    def hit(self, state, code):
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

    def hit_winner(self, state, code):
        if len(state.winners()) == 1:
            self.say('Checked out! You are the winner')
        else:
            self.say('Checked out! You are number %d' % (len(state.winners())))

    def enter_hold(self, *args):
        sleep(0.5)
        self.say('Press START')

    def round_started(self, state):
        self.say('Next player. Is. %s.' % ('.'.join(state.players[state.currentPlayer])))
