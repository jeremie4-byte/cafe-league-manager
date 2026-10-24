from datetime import time
from services.validators import validate_positive_id, validate_schedule_time

"""Creating Match class with all SQL attributes"""
class Match:
    def __init__(self, match_id, event_id, schedule_match_time: time):
        self.match_id =  validate_positive_id(match_id)
        self.event_id =  validate_positive_id(event_id)
        self.schedule_match_time = validate_schedule_time(schedule_match_time)
