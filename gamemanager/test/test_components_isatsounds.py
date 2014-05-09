from components.isatsounds import *
from game import GameState
import unittest

class TestSounds(unittest.TestCase):
    def setUp(self):
        self.mock_1 = GameState(['AB', 'CD'], 301, 'fake1', True)
        self.mock_1.advance_player()
        self.mock_1.add_dart('T20', 60)
        self.mock_1.add_dart('T20', 60)
        self.snd = ISATSounds(test=True)

    def test_events_0(self):
        methods = ['DartStuck', 'ManualNextPlayer', 'EnterHold']
        for m in methods:
            getattr(self.snd, m)()

    def test_events_1(self):
        methods = ['FrameStarted']
        for m in methods:
            getattr(self.snd, m)(self.mock_1)        

    def test_events_2(self):
        methods = ['Hit', 'HitBust', 'HitWinner']
        for m in methods:
            getattr(self.snd, m)(self.mock_1, 'T20')    
