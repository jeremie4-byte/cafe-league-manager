from domains.match import Match
import unittest
from datetime import time
from services.validators import validate_positive_id, validate_schedule_time

class TestMatch(unittest.TestCase):

    """Test to see that a valid Match instance dan be generated"""
    def setUp(self):
        self.match = Match(1, 1, time(10, 30))

    """Test to see if 0 is accepted as a valid match_id"""
    def test_0_match_id(self):
        match2 = Match(0, 2, time(20, 45))
        self.assertEqual(match2.match_id, 0)

    """Test to see that a value error is raised if a match_id is below 0"""
    def test_invalid_match_id(self):
        with self.assertRaises(ValueError):
            match3 = Match(-500, 3, time(11, 45))

    """Test to see that a valid match instance can be generated"""
    def test_valid_match_id(self):
        match4 = Match(2, 4, time(13, 25))
        self.assertEqual(match4.match_id, 2)

    """Test to see if 0 is accepted as an event_id"""
    def test_0_event_id(self):
        match5 = Match(3, 0, time(14))
        self.assertEqual(match5.event_id, 0)

    """Test to see that a value error is raised if an event_id is below 0"""
    def test_invalid_event_id(self):
        with self.assertRaises(ValueError):
            match6 = Match(4, -20, time(16, 30))

    """Test to see that a valid event id is accepted and genertated"""
    def test_valid_event_id(self):
        match7 = Match(5, 4, time(18, 50))
        self.assertEqual(match7.event_id, 4)

    """Test to see that an unvalid time outside of 10 to 22 is not accepted"""
    def test_invalid_business_schedule_time(self):
        with self.assertRaises(ValueError):
            schedule_time = time(23, 30)
            validate_schedule_time(schedule_time)

    """Boundary test to see that time at 10 and 22 are accepted"""
    def test_valid_boundary_schedule_time(self):
        lower_boundary = time(10)
        valid_lower_boundary = validate_schedule_time(lower_boundary)
        self.assertEqual(valid_lower_boundary, time(10))
        upper_boundary = time(22)
        valid_upper_boundary = validate_schedule_time(upper_boundary)
        self.assertEqual(valid_upper_boundary, time(22))

    """Boundary test to see that time at 9:59AM and 22:01 raise ValueErrors"""
    def test_invalid_boundary_schedule_time(self):
        with self.assertRaises(ValueError):
            lower_boundary = time(9, 59)
            validate_schedule_time(lower_boundary)
        with self.assertRaises(ValueError):
            upper_boundary = time(22, 1)
            validate_schedule_time(upper_boundary)

    """Test to see that invalid time formats raise the expected TypeError"""
    def test_invalid_time_format(self):
        with self.assertRaises(TypeError):
            validate_schedule_time("20")

    """Test to see that a valid time format for scheduele_match_time is accepted"""
    def test_valid_scheduele_time(self):
        schedule_time = time(19, 35)
        valid_schedule_time = validate_schedule_time(schedule_time)
        self.assertEqual(valid_schedule_time, time(19, 35)) 
