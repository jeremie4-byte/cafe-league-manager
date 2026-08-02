import unittest

from domains.player import Player, PlayerType
from domains.match_player import MatchPlayer, MatchResult, Attendance
from domains.elo import EloCalculation, K_FACTOR
from domains.event import EventType
from datetime import datetime

class TestEloCalculation(unittest.TestCase):

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

        """Test to see that negative elo raises a Type Error without applying the gains formula"""
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

    def test_elo_outcome_2_players(self):
        """We build our 2 Player objects to test"""
        winning_player = Player(1, "Jeremie Lortie", PlayerType.LEAGUE_REGULAR, datetime(2025, 11, 4), 2000)
        losing_player = Player(2, "Isis Montaño", PlayerType.LEAGUE_REGULAR, datetime(2025, 4, 9), 3000)
        
        """We build the match results"""
        winning_match_player = MatchPlayer(1, 1, MatchResult.FIRST_PLACE, Attendance.ATTENDED)
        losing_match_player = MatchPlayer(2, 1, MatchResult.SECOND_PLACE, Attendance.ATTENDED)
       
        """We create the player list and match_players_list to pass into our elo_outcome function"""
        player_list = [winning_player, losing_player]
        match_players_list = [winning_match_player, losing_match_player]

        """We now insert the lists intot our function to make sure Jeremie wins elo and Isis loses elo"""
        updated_players, elo_changes = EloCalculation.elo_outcome(player_list, match_players_list, EventType.RANKED_LEAGUE_MATCH)

        """We verify to see that Jeremie has now more than 2000 elo and Isis has now less than 3000 elo"""
        self.assertGreater(winning_player.current_elo, 2000)
        self.assertLess(losing_player.current_elo, 3000)

    def test_elo_outcome_1_active_player(self):

        """We build an invalid 1 player object to test for elo changes"""
        player = Player(3, "Devin Wiksburgen", PlayerType.TOURNAMENT_COMPETITOR, datetime(2026, 2, 13), 1500)

        """We build his invalid match result"""
        player_result = MatchPlayer(3, 2, MatchResult.FIRST_PLACE, Attendance.ATTENDED)

        """We build the player and results list"""
        player_list = [player]
        match_players_list = [player_result]

        """We test to see that a Value Error will be raised"""
        with self.assertRaises(ValueError):
             updated_players, elo_changes = EloCalculation.elo_outcome(player_list, match_players_list, EventType.TOURNAMENT_MATCH)

    def test_cancelled_2_player_match(self):

        """We build 2 player objects where one player attended and the other cancelled"""
        attended_player = Player(4, "John Doe", PlayerType.LEAGUE_REGULAR, datetime(2026, 3, 28), 3500)
        cancelled_player = Player(5, "Jane Doe", PlayerType.TOURNAMENT_COMPETITOR, datetime(2025, 6, 19), 2500)

        """We build the results even if one player cancelled"""
        attended_match__player = MatchPlayer(4, 3, MatchResult.FIRST_PLACE, Attendance.ATTENDED)
        cancelled_match_player = MatchPlayer(5, 3, MatchResult.NONE, Attendance.CANCELLED)

        """We build the player and results list"""
        player_list = [attended_player, cancelled_player]
        match_players_list = [attended_match__player, cancelled_match_player]

        """We verify that no elo changes will be made and that an error will be raised instead"""
        with self.assertRaises(ValueError):
            updated_players, elo_changes = EloCalculation.elo_outcome(player_list, match_players_list, EventType.TOURNAMENT_MATCH)

    def test_no_show_2_player_match(self):

        """We build 2 player objects where one player attended and the other one no showed"""
        attended_player = Player(6, "Myriam De Grandpé", PlayerType.LEAGUE_REGULAR, datetime(2025, 12, 17), 2000)
        no_show_player = Player(7, "Johnny Themstack", PlayerType.LEAGUE_REGULAR, datetime(2026, 7, 26), 1000)

        """We build the results even if one player did a no show"""
        attended_match_player = MatchPlayer(6, 4, MatchResult.FIRST_PLACE, Attendance.ATTENDED)
        no_show_match_player = MatchPlayer(7, 4, MatchResult.NONE, Attendance.NO_SHOW)

        """We build the player and results list"""
        player_list = [attended_player, no_show_player]
        match_players_list = [attended_match_player, no_show_match_player]

        """We verify that no elo changes will be made and that an error will be raised instead"""
        with self.assertRaises(ValueError):
            updated_players, elo_changes = EloCalculation.elo_outcome(player_list, match_players_list, EventType.RANKED_LEAGUE_MATCH)

    def test_uneven_match_results_and_players(self):
        
        """We build 2 player object"""
        player1 = Player(8, "Romeo Gomez", PlayerType.LEAGUE_REGULAR, datetime(2026, 5, 22), 2500)
        player2 = Player(9, "Johanna Montigny", PlayerType.LEAGUE_REGULAR, datetime(2026, 1, 8), 3500)

        """We build only one Match Result"""
        match_player1 = MatchPlayer(8, 5, MatchResult.FIRST_PLACE, Attendance.ATTENDED)

        """We build the player and results list"""
        player_list = [player1, player2]
        match_players_list = [match_player1]

        """We test to see that a Value Error is generated for the uneven player list and player results"""
        with self.assertRaises(ValueError):
            updated_players, elo_changes = EloCalculation.elo_outcome(player_list, match_players_list, EventType.RANKED_LEAGUE_MATCH)

    def test_mismatched_player_and_match_player_id(self):

        """We build 2 player objects"""
        player1 = Player(10, "Karl Marshall", PlayerType.LEAGUE_REGULAR, datetime(2025, 10, 7), 500)
        player2 = Player(11, "Phillip Trottier", PlayerType.LEAGUE_REGULAR, datetime(2025, 9, 19), 3600)

        """We build Match results with the wrong player ids"""
        match_player1 = MatchPlayer(12, 6, MatchResult.FIRST_PLACE, Attendance.ATTENDED)
        match_player2 = MatchPlayer(13, 6, MatchResult.SECOND_PLACE, Attendance.ATTENDED)

        """We build the player and the results list"""
        player_list = [player1, player2]
        match_players_list = [match_player1, match_player2]

        """We test to see that a Value Error is generated for the mismatched of player ID between the player and match_player objects"""
        with self.assertRaises(ValueError):
            updated_players, elo_changes = EloCalculation.elo_outcome(player_list, match_players_list, EventType.TOURNAMENT_MATCH)

    def test_upper_4000_elo_boundary(self):

        """We build 2 player objects both with 4000 elos"""
        player1 = Player(13, "Sarah Bertrand", PlayerType.LEAGUE_REGULAR, datetime(2024, 12, 12), 4000)
        player2 = Player(14, "Yu Nguyen", PlayerType.LEAGUE_REGULAR, datetime(2025, 2, 3), 4000)

        """We build the match results"""
        match_player_1 = MatchPlayer(13, 7, MatchResult.FIRST_PLACE, Attendance.ATTENDED)
        match_player2 = MatchPlayer(14, 7, MatchResult.SECOND_PLACE, Attendance.ATTENDED)

        """We build the player and the results list"""
        player_list = [player1, player2]
        match_players_list = [match_player_1, match_player2]

        updated_players, elo_changes = EloCalculation.elo_outcome(player_list, match_players_list, EventType.RANKED_LEAGUE_MATCH)

        """We test to see that player 1's score does not exceed 4000 as it is our elo maximum"""
        self.assertEqual(player1.current_elo, 4000)

    def test_lower_0_elo_boundary(self):

        """We build 2 player objects with 0 elo"""
        player1 = Player(15, "Kenneth McLaud", PlayerType.LEAGUE_REGULAR, datetime(2026, 7, 26), 0)
        player2 = Player(16, "Daniela Torrealba", PlayerType.LEAGUE_REGULAR, datetime(2026, 7, 26), 0)

        """We build the match results"""
        match_player_1 = MatchPlayer(15, 8, MatchResult.FIRST_PLACE, Attendance.ATTENDED)
        match_player_2 = MatchPlayer(16, 8, MatchResult.SECOND_PLACE, Attendance.ATTENDED)

        """We build the player and the results list"""
        player_list = [player1, player2]
        match_players_list = [match_player_1, match_player_2]

        updated_players, elo_changes = EloCalculation.elo_outcome(player_list, match_players_list, EventType.TOURNAMENT_MATCH)

        """We test to see that player 2's score does not go below 0 as it is our elo minimum"""
        self.assertEqual(player2.current_elo, 0)


    def test_elo_outcome_multiplayer_match(self):

        """We build 8 players"""
        player1 = Player(17, "Benoit Trottier", PlayerType.LEAGUE_REGULAR, datetime(2025, 9, 18), 1500)
        player2 = Player(18, "Katie Sintorc", PlayerType.LEAGUE_REGULAR, datetime(2026, 6, 21), 1500)
        player3 = Player(19, "Kyra Provencal", PlayerType.LEAGUE_REGULAR, datetime(2026, 5, 30), 1500)
        player4 = Player(20 , "Cameron Charlton", PlayerType.LEAGUE_REGULAR, datetime(2025, 7, 1), 1500)
        player5 = Player(21, "Christian Champagne", PlayerType.LEAGUE_REGULAR, datetime(2025, 4, 19), 1500)
        player6 = Player(22, "Firinn Wylde", PlayerType.LEAGUE_REGULAR, datetime(2026, 1, 11), 1500)
        player7 = Player(23, "Jason Langlois", PlayerType.LEAGUE_REGULAR, datetime(2026, 2, 2), 1500)
        player8 = Player(24, "Lea Schramm", PlayerType.LEAGUE_REGULAR, datetime(2026, 5, 25), 1500)

        "We build the match results"
        match_player1 = MatchPlayer(17, 9, MatchResult.FIRST_PLACE, Attendance.ATTENDED)
        match_player2 = MatchPlayer(18, 9, MatchResult.SECOND_PLACE, Attendance.ATTENDED)
        match_player3 = MatchPlayer(19, 9, MatchResult.THIRD_PLACE, Attendance.ATTENDED)
        match_player4 = MatchPlayer(20, 9, MatchResult.FOURTH_PLACE, Attendance.ATTENDED)
        match_player5 = MatchPlayer(21, 9, MatchResult.FIFTH_PLACE, Attendance.ATTENDED)
        match_player6 = MatchPlayer(22, 9, MatchResult.SIXTH_PLACE, Attendance.ATTENDED)
        match_player7 = MatchPlayer(23, 9, MatchResult.SEVENTH_PLACE, Attendance.ATTENDED)
        match_player8 = MatchPlayer(24, 9, MatchResult.EIGHT_PLACE, Attendance.ATTENDED)

        """We build the player and results list"""
        player_list = [player1, player2, player3, player4, player5, player6, player7, player8]
        match_players_list = [match_player1, match_player2, match_player3, match_player4, match_player5, match_player6, match_player7, match_player8]

        """We run our static method"""
        updated_players, elo_changes = EloCalculation.elo_outcome(player_list, match_players_list, EventType.RANKED_LEAGUE_MATCH)

        """we verify that each place has more elo than the one below it"""
        self.assertGreater(player1.current_elo, player2.current_elo)
        self.assertGreater(player2.current_elo, player3.current_elo)
        self.assertGreater(player3.current_elo, player4.current_elo)
        self.assertGreater(player4.current_elo, player5.current_elo)
        self.assertGreater(player5.current_elo, player6.current_elo)
        self.assertGreater(player6.current_elo, player7.current_elo)
        self.assertGreater(player7.current_elo, player8.current_elo)

    def test_equal_multiplayer_elo_outcome(self):

        """We build 4 players"""
        player1 = Player(25, "Isabelle Cadic", PlayerType.LEAGUE_REGULAR, datetime(2026, 2, 12), 1500)
        player2 = Player(26, "Flavien Pacary", PlayerType.LEAGUE_REGULAR, datetime(2026, 4, 14), 1500)
        player3 = Player(27, "David Rousseau", PlayerType.LEAGUE_REGULAR, datetime(2025, 11, 16), 1500)
        player4 = Player(28, "Corinne Palisse", PlayerType.LEAGUE_REGULAR, datetime(2026, 1, 17), 1500)

        """We build equal test results"""
        match_player1 = MatchPlayer(25, 10, MatchResult.FIRST_PLACE, Attendance.ATTENDED)
        match_player2 = MatchPlayer(26, 10, MatchResult.FIRST_PLACE, Attendance.ATTENDED)
        match_player3 = MatchPlayer(27, 10, MatchResult.FIRST_PLACE, Attendance.ATTENDED)
        match_player4 = MatchPlayer(28, 10, MatchResult.FIRST_PLACE, Attendance.ATTENDED)

        """We build the player and results list"""
        player_list = [player1, player2, player3, player4]
        match_players_list = [match_player1, match_player2, match_player3, match_player4]

        """We run our static method"""
        updated_players, elo_changes = EloCalculation.elo_outcome(player_list, match_players_list, EventType.TOURNAMENT_MATCH)

        """We verify that all updated elo outcomes are equal"""
        self.assertEqual(player1.current_elo, player2.current_elo)
        self.assertEqual(player1.current_elo, player3.current_elo)
        self.assertEqual(player1.current_elo, player4.current_elo)

    def test_partially_attended_multiplayer_match(self):

        """We build 4 players"""
        player1 = Player(29, "Michael Durap", PlayerType.LEAGUE_REGULAR, datetime(2026, 6, 29), 1500)
        player2 = Player(30, "Nicholas Lamontagne", PlayerType.LEAGUE_REGULAR, datetime(2025, 8, 23), 1500)
        player3 = Player(31, "Stacy Irving", PlayerType.LEAGUE_REGULAR, datetime(2025, 9, 18), 1500)
        player4 = Player(32, "Matthew McKnight", PlayerType.LEAGUE_REGULAR, datetime(2026, 3, 1), 1500)

        """We build match players with one player that cancelled, and one that was a no-show"""
        match_player1 = MatchPlayer(29, 11, MatchResult.FIRST_PLACE, Attendance.ATTENDED)
        match_player2 = MatchPlayer(30, 11, MatchResult.NONE, Attendance.CANCELLED)
        match_player3 = MatchPlayer(31, 11, MatchResult.NONE, Attendance.NO_SHOW)
        match_player4 = MatchPlayer(32, 11, MatchResult.SECOND_PLACE, Attendance.ATTENDED)

        """We build the player list and results list"""
        player_list = [player1, player2, player3, player4]
        match_players_list = [match_player1, match_player2, match_player3, match_player4]

        """We run our static method"""
        updated_players, elo_changes = EloCalculation.elo_outcome(player_list, match_players_list, EventType.RANKED_LEAGUE_MATCH)

        """We test that player2 and player3 elo remain unchanged while testing that player 1's elo is greater than player 4"""
        self.assertGreater(player1.current_elo, player4.current_elo)
        self.assertEqual(player2.current_elo, 1500)
        self.assertEqual(player3.current_elo, 1500)

    def test_open_game_night_skips_elo(self):
        """ Open Game Night events should return players unchanged with no elo_update entries"""
        player1 = Player(33, "Test Player A", PlayerType.LEAGUE_REGULAR, datetime(2026, 1, 1), 1500)
        player2 = Player(34, "Test Player B", PlayerType.LEAGUE_REGULAR, datetime(2026, 1, 1), 1500)

        match_player1 = MatchPlayer(33, 12, MatchResult.FIRST_PLACE, Attendance.ATTENDED)
        match_player2 = MatchPlayer(34, 12, MatchResult.SECOND_PLACE, Attendance.ATTENDED)

        player_list = [player1, player2]
        match_players_list = [match_player1, match_player2]

        updated_players, elo_changes = EloCalculation.elo_outcome(player_list, match_players_list, EventType.OPEN_GAME_NIGHT)

        self.assertEqual(elo_changes, {})
        self.assertEqual(player1.current_elo, 1500)
        self.assertEqual(player2.current_elo, 1500)
