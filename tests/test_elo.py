import unittest

from domains.player import Player
from domains.match_player import MatchPlayer, MatchResult, Attendance
from domains.elo import EloCalculation, K_FACTOR

class testEloCalculation(unittest.TestCase):

    def test_probabilistic_elo_equal_ratings(self):
        """Equal ratings should result in an approximate 50% win probability for both players"""
        prob_a, prob_b = EloCalculation.probabilistic_elo(1000, 1000)
        self.assertAlmostEqual(prob_a, 0.5)
        self.assertAlmostEqual(prob_b, 0.5)

    def test_0_elo_equal_ratings(self):
        """0 value for elo should be accepted and return am approximate 50% win if both players have that score"""
        prob_a, prob_b = EloCalculation.probabilistic_elo(0, 0)
        self.assertAlmostEqual(prob_a, 0.5)
        self.assertAlmostEqual(prob_b, 0.5)

    def test_4000_elo_equal_ratings(self):
        """4000 value for elo should be accepted and return am approximate 50% win if both players have that score"""
        prob_a, prob_b = EloCalculation.probabilistic_elo(4000, 4000)
        self.assertAlmostEqual(prob_a, 0.5)
        self.assertAlmostEqual(prob_b, 0.5)

    def test_negative_elo_raises_error (self):

        """Test to see that negative elo raises a Value Error without applying the gains formula"""
        with self.assertRaises(ValueError):
            EloCalculation.probabilistic_elo(-500, 3219)

        with self.assertRaises(ValueError):
            EloCalculation.probabilistic_elo(1678, -2000)

    def test_over4000_elo_raises_error(self):

        """Test to see that over 4000 elo raises a Value Error without applying the gains formula"""
        with self.assertRaises(ValueError):
            EloCalculation.probabilistic_elo(5000, 1245)

        with self.assertRaises(ValueError):
            EloCalculation.probabilistic_elo(3476, 5000)

    def test_probabilistic_elo_heteregeneous_score(self):
        """A 400-point advantage should give ~90.91% win probability (10:1 expected score)"""
        # 1400 vs 1000 rating gap = 10^(400/400) = 10x higher odds
        prob_a, prob_b = EloCalculation.probabilistic_elo(1400, 1000)

        # Win probability for 400 point gap is 1 / (1 + 10^-1) = 10/11 ≈ 0.9090909
        self.assertAlmostEqual(prob_a, 0.9090909, places=6)
        self.assertAlmostEqual(prob_b, 0.0909091, places=6)
        
        # Sanity check: sum of probabilities must always equal 1.0 (100%)
        self.assertAlmostEqual(prob_a + prob_b, 1.0)
