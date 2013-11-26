""" Espeak output """

from espeak import espeak
from circuits import Component
from time import sleep
from namemapping import name_mapping

class EspeakSounds(Component):
    def __init__(self):
        super(EspeakSounds, self).__init__()
        espeak.set_voice('en/en-sc')

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
            if code.endswith('i'):
                code = code[:-1]
            self.say(code[1:])

    def HitBust(self, *args):
        self.say('Bust')

    def HitWinner(self, state, code):
        if len(state.winners()) == 0:
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
