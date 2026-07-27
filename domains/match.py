from datetime import datetime
from services.validators import *

"""Creating Match class with all SQL attributes"""
class Match:
    def __init__(self, match_id, event_id, schedule_match_time: datetime):
        self.match_id =  validate_positive_id(match_id)
        self.event_id =  validate_positive_id(event_id)
        self.schedule_match_time = validate_datetime_format(schedule_match_time)
