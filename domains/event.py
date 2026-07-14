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
        self.event_name = event_name
        self.event_type = event_type
        self.game_title = game_title
        self.event_capacity = event_capacity
        self.event_date = event_date
