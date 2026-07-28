from domains.match_player import MatchPlayer, MatchResult, Attendance
import unittest
from enum import Enum

class TestMatchPlayer (unittest.TestCase):

    """Default test case where all conditions are met"""
    def setUp(self):
        self.match_player = MatchPlayer(1, 1, MatchResult.FIRST_PLACE, Attendance.ATTENDED)

    def test_default_case(self):
        self.assertEqual(self.match_player.player_id, 1)
        self.assertEqual(self.match_player.match_id, 1)
        self.assertEqual(self.match_player.match_result, MatchResult.FIRST_PLACE)
        self.assertEqual(self.match_player.attendance, Attendance.ATTENDED)

    """Test to see that 0 is an accepted player id value"""
    def test_valid_0player_id(self):
        match_player2 = MatchPlayer(0, 2, MatchResult.SECOND_PLACE, Attendance.ATTENDED)
        self.assertEqual(match_player2.player_id, 0)

    """Test to see that valid player_id are accepted"""
    def test_valid_player_id(self):
        match_player3 = MatchPlayer(2, 3, MatchResult.THIRD_PLACE, Attendance.ATTENDED)
        self.assertEqual(match_player3.player_id, 2)

    """Test invalid player id raises a ValueError"""
    def test_invalid_player_id(self):
        with self.assertRaises(ValueError):
            match_player4 = MatchPlayer(-500, 4, MatchResult.FOURTH_PLACE, Attendance.ATTENDED)

    """Test to see that 0 is an accepted match id value"""
    def test_valid_0match_id(self):
        match_player5 = MatchPlayer(3, 0, MatchResult.FIFTH_PLACE, Attendance.ATTENDED)
        self.assertEqual(match_player5.match_id, 0)

    """Test to see that valid match id are accepted"""
    def test_valid_match_id(self):
        match_player6 = MatchPlayer(4, 5, MatchResult.SIXTH_PLACE, Attendance.ATTENDED)
        self.assertEqual(match_player6.match_id, 5)

    """Test invalid match id raises a ValueError"""
    def test_invalid_match_id(self):
        with self.assertRaises(ValueError):
            match_player7 = MatchPlayer(5, -100, MatchResult.SEVENTH_PLACE, Attendance.ATTENDED)

    """Test that match result FIRST_PLACE is accepted"""
    def test_first_place(self):
        match_player8 = MatchPlayer(6, 6, MatchResult.FIRST_PLACE, Attendance.ATTENDED)
        self.assertEqual(match_player8.match_result, MatchResult.FIRST_PLACE)

    """Test that match result SECOND_PLACE is accepted"""
    def test_second_place(self):
        match_player9 = MatchPlayer(7, 7, MatchResult.SECOND_PLACE, Attendance.ATTENDED)
        self.assertEqual(match_player9.match_result, MatchResult.SECOND_PLACE)

    """Test that match result THIRD_PLACE is accepted"""
    def test_third_place(self):
        match_player10 = MatchPlayer(8, 8, MatchResult.THIRD_PLACE, Attendance.ATTENDED)
        self.assertEqual(match_player10.match_result, MatchResult.THIRD_PLACE)

    """Test that match result FOURTH_PLACE is accepted"""
    def test_fourth_place(self):
        match_player11 = MatchPlayer(9, 9, MatchResult.FOURTH_PLACE, Attendance.ATTENDED)
        self.assertEqual(match_player11.match_result, MatchResult.FOURTH_PLACE)

    """Test that match result FIFTH_PLACE is accepted"""
    def test_fifth_place(self):
        match_player12 = MatchPlayer(10, 10, MatchResult.FIFTH_PLACE, Attendance.ATTENDED)
        self.assertEqual(match_player12.match_result, MatchResult.FIFTH_PLACE)

    """Test that match result SIXTH_PLACE is accepted"""
    def test_sixth_place(self):
        match_player13 = MatchPlayer(11, 11, MatchResult.SIXTH_PLACE, Attendance.ATTENDED)
        self.assertEqual(match_player13.match_result, MatchResult.SIXTH_PLACE)

    """Test that match result SEVENTH_PLACE is accepted"""
    def test_seventh_place(self):
        match_player14 = MatchPlayer(12, 12, MatchResult.SEVENTH_PLACE, Attendance.ATTENDED)
        self.assertEqual(match_player14.match_result, MatchResult.SEVENTH_PLACE)

    """Test that match result EIGHT_PLACE is accepted"""
    def test_eight_place(self):
        match_player15 = MatchPlayer(13, 13, MatchResult.EIGHT_PLACE, Attendance.ATTENDED)
        self.assertEqual(match_player15.match_result, MatchResult.EIGHT_PLACE)

    """Test that an invalid match result raises an unvalid TypeError"""
    def test_invalid_place(self):
        with self.assertRaises(TypeError):
            match_player16 = MatchPlayer(14, 14, "9th Place", Attendance.NO_SHOW)

    """Test that attendance value 'Attended' is accepted"""
    def test_match_attended(self):
        match_player17 = MatchPlayer(15, 15, MatchResult.FIRST_PLACE, Attendance.ATTENDED)
        self.assertEqual(match_player17.attendance, Attendance.ATTENDED)

    """Test that attendance value 'Cancelled' is accepted"""
    def test_match_cancelled(self):
        match_player18 = MatchPlayer(16, 16, MatchResult.NONE, Attendance.CANCELLED)
        self.assertEqual(match_player18.attendance, Attendance.CANCELLED)

    """Test that attendance value 'No Show' is accepted"""
    def test_match_no_show(self):
        match_player19 = MatchPlayer(17, 17, MatchResult.NONE, Attendance.NO_SHOW)
        self.assertEqual(match_player19.attendance, Attendance.NO_SHOW)

    """Test that an invalid attendance entry raises a TypeeError"""
    def test_invalid_match_attendance(self):
        with self.assertRaises(TypeError):
            match_player20 = MatchPlayer(18, 18, MatchResult.SEVENTH_PLACE, 'Postponed')
