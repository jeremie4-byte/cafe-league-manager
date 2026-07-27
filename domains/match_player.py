from enum import Enum
from services.validators import *

"""Creating an Enum class for all different SQL match_result"""
class MatchResult(Enum):
    FIRST_PLACE = ("1st Place", 1)
    SECOND_PLACE = ("2nd Place", 2)
    THIRD_PLACE = ("3rd Place", 3)
    FOURTH_PLACE = ("4th Place", 4)
    FIFTH_PLACE = ("5th Place", 5)
    SIXTH_PLACE = ("6th Place", 6)
    SEVENTH_PLACE = ("7th Place", 7)
    EIGHT_PLACE = ("8th Place", 8)
    NONE = ("None", None)

"""Creating an Enum class for all different SQL attendance"""
class Attendance(Enum):
    ATTENDED = "Attended"
    NO_SHOW = "No-Show"
    CANCELLED = "Cancelled"

"""Creating match_player SQL table as a class"""
class MatchPlayer:
    def __init__(self, player_id, match_id, match_result: MatchResult, attendance: Attendance):
        self.player_id = validate_positive_id(player_id)
        self.match_id = validate_positive_id(match_id)
        if not isinstance(match_result, MatchResult):
            raise TypeError("match_result must be a valid MatchResult enum instance")
        
        if not isinstance(attendance, Attendance):
            raise TypeError("attendance must be a valid Attendance enum instance")
        
        if attendance in(Attendance.NO_SHOW, Attendance.CANCELLED):
           match_result = MatchResult.NONE
        
        self.attendance = attendance
        self.match_result = match_result
