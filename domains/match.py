from datetime import datetime

"""Creating Match class with all SQL attributes"""
class Match:
    def __init__(self, match_id, event_id, schedule_match_time: datetime):
        self.match_id = match_id
        self.event_id = event_id
        self.schedule_match_time = schedule_match_time
