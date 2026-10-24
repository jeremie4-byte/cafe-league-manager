from datetime import date, datetime, time

EARLIEST_START_TIME = time(10, 0)
LATEST_START_TIME = time(22, 0)
# Business hours are from (9AM to 23PM), Events ,must start from 10AM until 10PM

"""Validator to ensure that no negative Id's are inputed"""
def validate_positive_id(value):
    if value < 0:
        raise ValueError("ID cannot be negative")
    
    return value
    
"""Validator to make sure that event name, game name, and player names are at least 5 chars"""
def validate_min_name_length(value):
    separator = " "
    username = separator.join(value.split())

    if len(username.replace(" ", "")) < 5:
        raise ValueError("Name, must be at least 5 characters!")
    
    return username

"""Validator for all join_date Cafe_Player attribute to ensure no player is created in the future"""
def validate_datetime_format(value):
    if not isinstance(value, datetime):
        raise TypeError("The entry isn't correctly formated as a datetime(YYYY, MM, DD)")
    
    if value > datetime.now():
        raise ValueError("Date cannot be in the future!")
    
    return value

"""Validator for event datetime objects to assure that events can be created with future dates."""
def validate_event_date(value):
    if not isinstance(value, date):
        raise TypeError("The entry must be a date(YYYY,MM,DD)")
    
    if isinstance(value, datetime):
        raise TypeError("The entry must be a date, not a datetime; the time belongs to the match")
    
    return value

"""Validator to ensure a valid elo score"""
def validate_elo_range(value):
    if value < 0 or value > 4000:
        raise ValueError("Elo scores must remain between 0 and 4000")
    
    return value

"""Validator to ensure valid event capacity"""
def validate_event_capacity(value):
    if value < 1 or value > 100:
        raise ValueError("Event capacity must be between 1 and 100")
    
    return value 

"""Validator function to sendure valid match schedule_match_time entries"""
def validate_schedule_time(value):
    if not isinstance(value, time):
        raise TypeError("The entry isn't correctly formatted as time(HH, MM, SS)")
    
    if not (EARLIEST_START_TIME <= value <= LATEST_START_TIME):
        raise ValueError("The scheduled time needs to start at or between 10AM to 10PM")
    
    return value
