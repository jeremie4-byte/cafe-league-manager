from enum import Enum
from datetime import datetime

"""Creating an Enum class for all different SQL event_type"""
class EventType(Enum):
    OPEN_GAME_NIGHT = "Open Game Night"
    RANKED_LEAGUE_MATCH = "Ranked League Match"
    TOURNAMENT_MATCH = "Tournament Match"

"""Creating Event class with all SQL attributes"""
class Event:
    def __init__(self, event_id, event_name, event_type: EventType, game_title, event_capacity, event_date: datetime):
        self.event_id = event_id
        if event_id < 0:
            raise ValueError
        self.event_name = event_name
        if event_name == "":
            raise ValueError
        self.event_type = event_type
        if event_type != "Open Game Night" and event_type != "Ranked League Match" and event_type != "Tournament Match":
            raise ValueError
        self.game_title = game_title
        if game_title == "":
            raise ValueError
        self.event_capacity = event_capacity
        if event_capacity < 1 or event_capacity > 100:
            raise ValueError
        self.event_date = event_date
        if not isinstance(event_date, datetime):
            raise ValueError
