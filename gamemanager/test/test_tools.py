from isat.tools import *
from darttools import *
from game import GameState
import unittest

class TestScore2sum(unittest.TestCase):
    def test(self):
        self.assertEqual(score2sum('D20'), 40)
        self.assertEqual(score2sum('D25'), 50)
        self.assertEqual(score2sum('S4i'), 4)
        self.assertEqual(score2sum('T20'), 60)
        self.assertEqual(score2sum('T1'), 3)

class TestCheckoutOptions(unittest.TestCase):
    def test(self):
        self.assertEquals(sorted(checkout_options(60)), ['T20'])
        self.assertEquals(sorted(checkout_options(24)), sorted(['D12', 'T8']))
        self.assertEquals(sorted(checkout_options(15)), sorted(['T5', 'S15']))
        self.assertEquals(sorted(checkout_options(6)), sorted(['S6', 'T2', 'D3']))

class TestFieldtexts(unittest.TestCase):
    
    def test(self):
        self.assertEqual(fieldtexts['code_D19'], ('Double 19!', 'happy'))

class TestInRing(unittest.TestCase):
    
    def test_a(self):
        assert in_ring(['S15i', 'D10', 'S2'])

    def test_b(self):
        assert in_ring(['D20', 'S1'])

    def test_c(self):
        assert in_ring(['S1i', 'D5', 'D20'])

    def test_d(self):
        assert not in_ring(['S16', 'T19'])

    def test_e(self):
        assert not in_ring(['S2i', 'D17', 'S19'])

    def test_f(self):
        assert not in_ring(['S2', 'S2', 'S15'])


class TestAdjacent(unittest.TestCase):
    
    def test_a(self):
        assert adjacent('S20', 'S5')

    def test_b(self):
        assert adjacent('S25', 'D25')

    def test_c(self):
        assert not adjacent('S25', 'S20')

    def test_d(self):
        assert adjacent('D5', 'D12')

    def test_e(self):
        assert not adjacent('D20', 'D12')

class TestConvenience(unittest.TestCase):
    def setUp(self):
        self.mock_1 = GameState(['AB', 'CD'], 301, 'fake1', True)
        self.mock_1.advance_player()
        self.mock_1.add_dart('T10', 30)

        self.mock_2 = GameState(['AB', 'CD'], 301, 'fake2', True)
        self.mock_2.advance_player()
        self.mock_2.add_dart('T10', 30)
        self.mock_2.add_dart('T10', 30)
        self.mock_2.add_dart('S1', 1)

    def test_a(self):
        self.assertEqual(('T10', 1, ['T10'], 301, 301, 271), convenience(self.mock_1))

    def test_b(self):
        self.assertEqual(('S1', 3, ['T10', 'T10', 'S1'], 301, 241, 240), convenience(self.mock_2))
