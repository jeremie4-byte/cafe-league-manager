from domains.match import Match
import unittest
from datetime import datetime

class TestMatch(unittest.TestCase):

    """Test to see that a valid Match instance dan be generated"""
    def setUp(self):
        self.match = Match(1, 1, datetime(2026, 7, 20))

    """Test to see if 0 is accepted as a valid match_id"""
    def test_0_match_id(self):
        match2 = Match(0, 2, datetime(2026, 6, 9))
        self.assertEqual(match2.match_id, 0)

    """Test to see that a value error is raised if a match_id is below 0"""
    def test_invalid_match_id(self):
        with self.assertRaises(ValueError):
            match3 = Match(-500, 3, datetime(2026, 1 ,2))

    """Test to see that a valid match instance can be generated"""
    def test_valid_match_id(self):
        match4 = Match(2, 4, datetime(2025, 11, 27))

    """Test to see if 0 is accepted as an event_id"""
    def test_0_event_id(self):
        match5 = Match(3, 0, datetime(2025, 12, 6))
        self.assertEqual(match5.event_id, 0)

    """Test to see that a value error is raised if an event_id is below 0"""
    def test_invalid_event_id(self):
        with self.assertRaises(ValueError):
            match6 = Match(4, -20, datetime(2024, 2, 27))

    """Test to see that a valid event id is accepted and genertated"""
    def test_valid_event_id(self):
        match7 = Match(5, 4, datetime(2026, 5, 30))
        self.assertEqual(match7.event_id, 4)

    """Test to see that an unvalid datetime format for scheduele_match_time is rejected"""
    def test_invalid_schedule_time(self):
        with self.assertRaises(ValueError):
            match8 = Match(6, 6, "2026-03-18")

    """Test to see that a valid datetime format for scheduele_match_time is accepted"""
    def test_valid_scheduele_time(self):
        match9 = Match(7, 7, datetime(2023, 3, 3))
        self.assertEqual(match9.schedule_match_time, datetime(2023, 3, 3))
