from enum import Enum
from datetime import datetime
from services.validators import *

"""Creating an Enum class for all different SQL event_type"""
class EventType(Enum):
    OPEN_GAME_NIGHT = "Open Game Night"
    RANKED_LEAGUE_MATCH = "Ranked League Match"
    TOURNAMENT_MATCH = "Tournament Match"

"""Creating Event class with all SQL attributes"""
class Event:
    def __init__(self, event_id, event_name, event_type: EventType, game_title, event_capacity, event_date: datetime):
        self.event_id = validate_positive_id(event_id)
        self.event_name = validate_min_name_length(event_name)
        if not isinstance(event_type, EventType):
            raise TypeError("event_type must be a valid EventType enum instance")
        self.event_type = event_type
        self.game_title = validate_min_name_length(game_title)
        self.event_capacity = validate_event_capacity(event_capacity)
        self.event_date = validate_datetime_format(event_date)
