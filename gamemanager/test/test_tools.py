from isat.tools import *
from game import GameState
import unittest

class TestFieldtexts(unittest.TestCase):
    
    def test(self):
        self.assertEqual(fieldtexts['code_D19'], ('Double 19!', 'happy'))

class TestInRing(unittest.TestCase):
    
    def test_a(self):
        assert in_ring([10, 15, 2])

    def test_b(self):
        assert in_ring([20, 1])

    def test_c(self):
        assert in_ring([5, 20, 1])

    def test_d(self):
        assert not in_ring([16, 19])

    def test_e(self):
        assert not in_ring([2, 17, 19])


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
        self.mock_1 = GameState(['AB', 'CD'], 301, 'fake1')
        self.mock_1.advance_player()
        self.mock_1.add_dart('T10', 30)

        self.mock_2 = GameState(['AB', 'CD'], 301, 'fake2')
        self.mock_2.advance_player()
        self.mock_2.add_dart('T10', 30)
        self.mock_2.add_dart('T10', 30)
        self.mock_2.add_dart('S1', 1)

    def test_a(self):
        self.assertEqual(('T10', 1, ['T10'], 301, 301, 271), convenience(self.mock_1))

    def test_b(self):
        self.assertEqual(('S1', 3, ['T10', 'T10', 'S1'], 301, 241, 240), convenience(self.mock_2))
