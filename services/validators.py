from datetime import datetime
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

"""Validator for all of our datetime objets to ensure correct formatting"""
def validate_datetime_format(value):
    if not isinstance(value, datetime):
        raise TypeError("The entry isn't correctly formatted (YYYY, MM, DD)")
    
    if value > datetime.now():
        raise ValueError("Date cannot be in the future!")
    
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
