from isat.rules import *
from isat.tools import isat_filename
from game import GameState
from os.path import exists
import unittest

class TestHit(unittest.TestCase):
    def setUp(self):
        self.mock_1 = GameState(['AB', 'CD'], 301, 'fake1', True)
        self.mock_1.advance_player()
        self.mock_1.add_dart('T20', 60)
        self.mock_1.add_dart('T20', 60)
        self.res = hit(self.mock_1)
        
    def test_a(self):
        assert len(self.res) > 0
        self.assertIn({'use': False, 'text': 'score_120', 'weight': 150}, self.res)

    def test_b(self):
        for e in self.res:
            self.assertIn(e['text'], texts)


class TestTexts(unittest.TestCase):
    def setUp(self):
        self.emotions = [
            'affectionate',	
            'afraid',	
            'amused',	
            'angry',	
            'bored',	
            'confident',	
            'content',	
            'disappointed',	
            'excited',	
            'happy',	
            'interested',	
            'loving',	
            'pleased',	
            'relaxed',	
            'sad',	
            'satisfied',	
            'worried'
            ]

    def test_a(self):
        for key, pair in texts.items():
            self.assertEquals(type(key), str)
            self.assertNotIn('/', key)
            self.assertIn(type(pair), [str, tuple, list])
            if type(pair) == list:
                for p in pair:
                    self._test_sound(key, p)
            else:
                self._test_sound(key, pair)

    def _test_sound(self, key, pair):
        if type(pair) == str:
            self.assertEquals(pair[0:4], 'wav:')
        else:
            self.assertEquals(len(pair), 2)
            text, emotion = pair
            self.assertEquals(type(text), str)
            self.assertIn(emotion, self.emotions)
        self.assertEquals(exists(isat_filename(key, pair)), True)
