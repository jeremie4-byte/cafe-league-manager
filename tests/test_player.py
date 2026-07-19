from domains.player import Player, PlayerType
import unittest
from datetime import datetime
from enum import Enum

class TestPlayer (unittest.TestCase):
    
    """Default test case to be tested"""
    def setUp(self):
        self.player = Player(1, "Jeremie Lortie", "Casual Drop-In", datetime(2026, 7, 19), 1500)

    """Test to see if Casual Drop-In is accepted"""
    def test_casual_drop_in(self):
        self.assertEqual(self.player.player_type, "Casual Drop-In")

    def test_league_regular(self):
        player2= Player(2, "Christina Cespedes", "League Regular", datetime(2021, 2, 7), 1307)
        self.assertEqual(player2.player_type, "League Regular")

    def test_tournament_competitor(self):
        player3 = Player(3, "Jessica Johnson", "Tournament Competitor", datetime(2023, 6, 25), 1673)
        self.assertEqual(player3.player_type, "Tournament Competitor")

    """We run deliberately a Player class with a 'Rookie' (non-accepted player type and wait for the assert to raise a value error)"""
    def test_player_type(self):
        with self.assertRaises(ValueError):
            player4 = Player(4, "Noah Lanston", "Rookie", datetime(2026, 6, 12), 1305)

    """We deliberately run a Player class without a datetime attribute for join_date to see if the system will raise a VelueError as expected"""
    def test_join_date(self):
        with self.assertRaises(ValueError):
            player5 = Player(5, "Diana Merchand", "League Regular", "2026-07-13", 1406)


    """Here we test to see that a value error raises if current elo isn't between 0 and 4000"""
    def test_wrong_elo(self):
        with self.assertRaises(ValueError):
            player6 = Player(6, "Erica Vieuxbled", "Tournament Competitor", datetime(2026, 5, 22), -500)

    """Unit test to see thqt the current elo of a player is within range"""
    def test_right_elo(self):
        player7 = Player(7, "Ebony Shapot", "League Regular", datetime(2025, 12, 21), 1200)
        self.assertEqual(player7.current_elo, 1200)

    """Unit test to see if a player with 0 elo score is accepted"""
    def test_0_elo(self):
        player8 = Player(8, "Christian Lauzon", "Casual Drop-In", datetime(2024, 11, 5), 0)
        self.assertEqual(player8.current_elo, 0)

    """Unit test to see if a player with 4000 elo score is accepted"""
    def test_4000_elo(self):
        player9 = Player(9, "Kim Stronglet", "Tournament Competitor", datetime(2022, 4, 17), 4000)
        self.assertEqual(player9.current_elo, 4000)
