from enum import Enum

"""Creating an Enum class for all different SQL match_result"""
class MatchResult(Enum):
    FIRST_PLACE = "1st Place"
    SECOND_PLACE = "2nd Place"
    THIRD_PLACE = "3rd Place"
    FOURTH_PLACE = "4th Place"
    FIFTH_PLACE = "5th Place"
    SIXTH_PLACE = "6th Place"
    SEVENTH_PLACE = "7th Place"
    EIGHT_PLACE = "8th Place"

"""Creating an Enum class for all different SQL attendance"""
class Attendance(Enum):
    ATTENDED = "Attended"
    NO_SHOW = "No-Show"
    CANCELLED = "Cancelled"

"""Creating match_player SQL table as a class"""
class MatchPlayer:
    def __init__(self, player_id, match_id, match_result: MatchResult, attendance: Attendance):
        self.player_id = player_id
        self.match_id = match_id
        self.match_result = match_result
        self.attendance = attendance
