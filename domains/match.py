from datetime import datetime

"""Creating Match class with all SQL attributes"""
class Match:
    def __init__(self, match_id, event_id, schedule_match_time: datetime):
        self.match_id = match_id
        if match_id < 0:
            raise ValueError
        self.event_id = event_id
        if event_id < 0:
            raise ValueError
        self.schedule_match_time = schedule_match_time
        if not isinstance(schedule_match_time, datetime):
            raise ValueError
