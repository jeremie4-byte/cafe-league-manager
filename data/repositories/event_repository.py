from data.db import get_connection
from datetime import date
from domains.event import Event, EventType
from services.validators import validate_event_date

def save_event_entry(event_entry: Event):
    """We first establish the db connection"""
    db_connection = get_connection()

    """We create the event_cursor to navigate and manipulate the match table"""
    event_cursor = db_connection.cursor()

    try:
        event_cursor.execute("""
        INSERT INTO Cafe_Event(event_id, event_name, event_type, game_title, event_capacity, event_date)
        VALUES(?, ?, ?, ?, ?, ?)
        """,
            (
            event_entry.event_id,
            event_entry.event_name,
            event_entry.event_type.value,
            event_entry.game_title,
            event_entry.event_capacity,
            event_entry.event_date.isoformat()
            )
        )

        new_entry = event_cursor.lastrowid

        db_connection.commit()
        print("event entry saved succesfully!")
        return new_entry
    
    except Exception as e:
        db_connection.rollback()
        print(f"Failed to insert event: {e} ")
        raise

    finally:
        db_connection.close()
    
def get_event_by_id(event_id: int):

    """We first establish the db connection"""
    db_connection = get_connection()

    """We create the event_cursor to navigate and manipulate the match table"""
    event_cursor = db_connection.cursor()

    try:
        event_cursor.execute(
        """
        SELECT event_id, event_name, event_type, game_title, event_capacity, event_date
        FROM Cafe_Event
        WHERE event_id = ?
        """,
            (event_id,)
        )

        event_row = event_cursor.fetchone()

        if event_row is not None: 
            event_entry = Event (
                event_row["event_id"],
                event_row["event_name"],
                EventType(event_row["event_type"]),
                event_row["game_title"],
                event_row["event_capacity"],
                date.fromisoformat(event_row["event_date"])
            )
            return event_entry
        
        else:
            raise ValueError(f"no event was found with event id: {event_id}")
        
    finally:
        db_connection.close()

def delete_event_by_id(event_id: int):

    """We first establish the db connection"""
    db_connection = get_connection()

    """We create the event_cursor to navigate and manipulate the match table"""
    event_cursor = db_connection.cursor()

    try:
        event_cursor.execute(
        """
        DELETE FROM Cafe_Event
        WHERE event_id = ?
        """,
            (event_id,)
        )

        row_affected = event_cursor.rowcount

        if row_affected == 0:
            raise ValueError(f"No event found with event id: {event_id}")
        
        else:
            db_connection.commit()
            print(f"Event with event ID {event_id} has been succesfully deleted!")
            return row_affected
    
    finally:
        db_connection.close()

def get_all_events():

    """We first establish the db connection"""
    db_connection = get_connection()

    """We create the event_cursor to navigate and manipulate the match table"""
    event_cursor = db_connection.cursor()

    try:
        event_cursor.execute(
            """
            SELECT event_id, event_name, event_type, game_title, event_capacity, event_date
            FROM Cafe_Event
            """
        )

        event_repository = event_cursor.fetchall()

        event_list = []

        for event_row in event_repository:
            event_entry = Event( 
                event_row["event_id"],
                event_row["event_name"],
                EventType(event_row["event_type"]),
                event_row["game_title"],
                event_row["event_capacity"],
                date.fromisoformat(event_row["event_date"])
            )
            event_list.append(event_entry)

        return event_list
    
    finally:
        db_connection.close()

def update_event_attributes(event_id: int, event_name: str | None = None, event_type: EventType | None = None, game_title: str | None = None, event_capacity: int | None = None, event_date: date | None = None):

    values=[]
    updated_field_entries=[]

    if event_name is not None: 
        updated_field_entries.append("event_name = ?")
        values.append(event_name)

    if event_type is not None: 
        updated_field_entries.append("event_type = ?")
        values.append(event_type.value)

    if game_title is not None: 
        updated_field_entries.append("game_title = ?")
        values.append(game_title)

    if event_capacity is not None:
        updated_field_entries.append("event_capacity = ?")
        values.append(event_capacity)

    if event_date is not None:
        validate_event_date(event_date)
        updated_field_entries.append("event_date = ?")
        values.append(event_date.isoformat())

    if len(values) == 0:
        raise ValueError(f"no fields were updated for event with event ID: {event_id}")
    
    new_fields = ", ".join(updated_field_entries)
    values.append(event_id)

    db_connection = get_connection()

    event_cursor = db_connection.cursor()

    try:
        event_cursor.execute (
            f"""
            UPDATE Cafe_Event
            SET {new_fields}
            WHERE event_id = ?
            """, tuple(values)
        )

        updated_event = event_cursor.rowcount

        if updated_event == 0:
            raise ValueError(f"Event with evnt ID {event_id} had no fields updated")
        
        else:
            db_connection.commit()
            print(f"Event with ID {event_id} was succesfully updated!")
            return updated_event
        
    except Exception as e:
        db_connection.rollback()
        print(f"Failed to update event because of error: {e}")
        raise
        
    finally:
        db_connection.close()

def get_event_by_name(event_name: str):

    """We first establish the db connection"""
    db_connection = get_connection()

    """We create the event_cursor to navigate and manipulate the event table"""
    event_cursor = db_connection.cursor()

    try:
        event_cursor.execute(
            """
            SELECT event_id, event_name, event_type, game_title, event_capacity, event_date
            FROM Cafe_Event
            WHERE event_name = ?
            """,
            (event_name,)
        )

        event_row = event_cursor.fetchone()

        if event_row is not None:
            event_entry = Event(
            event_row["event_id"],
            event_row["event_name"],
            EventType(event_row["event_type"]),
            event_row["game_title"],
            event_row["event_capacity"],
            date.fromisoformat(event_row["event_date"])
        )
            return event_entry
    
        else:
            raise ValueError(f"No event found with event name: {event_name}")
        
    finally:
        db_connection.close()

def get_event_by_type(event_type: EventType):

    """We first establish the db connection"""
    db_connection = get_connection()

    """We create the event_cursor to navigate and manipulate the event table"""
    event_cursor = db_connection.cursor()

    try:
        event_cursor.execute(
            """
            SELECT event_id, event_name, event_type, game_title, event_capacity, event_date
            FROM Cafe_Event
            WHERE event_type = ? 
            """,
            (event_type.value,)
        )

        event_type_entries = event_cursor.fetchall()

        event_type_list = []

        for event_row in event_type_entries:
            event = Event(
                event_row ["event_id"],
                event_row ["event_name"],
                EventType(event_row ["event_type"]),
                event_row ["game_title"],
                event_row ["event_capacity"],
                date.fromisoformat(event_row["event_date"])
            )
            event_type_list.append(event)
        
        return event_type_list
    
    finally:
        db_connection.close()


def get_event_by_game_title(game_title: str):

    """We first establish the db connection"""
    db_connection = get_connection()

    """We create the event_cursor to navigate and manipulate the event table"""
    event_cursor = db_connection.cursor()

    try: 
        event_cursor.execute(
            """
            SELECT event_id, event_name, event_type, game_title, event_capacity, event_date
            FROM Cafe_Event
            WHERE game_title = ? 
            """,
            (game_title,)
        )

        game_entries = event_cursor.fetchall()

        event_list = []

        for event in game_entries:
            event_entry = Event(
                event["event_id"],
                event["event_name"],
                EventType(event["event_type"]),
                event["game_title"],
                event["event_capacity"],
                date.fromisoformat(event["event_date"])
            )
            event_list.append(event_entry) 

        return event_list

    finally:
        db_connection.close()     

def get_event_by_date(event_date: date):

    """We first establish the db connection"""
    db_connection = get_connection()

    """We create the event_cursor to navigate and manipulate the event table"""
    event_cursor = db_connection.cursor()

    try:
        event_cursor.execute(
            """
            SELECT event_id, event_name, event_type, game_title, event_capacity, event_date
            FROM Cafe_Event
            WHERE event_date = ?
            """,
            (event_date.isoformat(),)
        )

        event_date_entries = event_cursor.fetchall()

        event_list = []

        for event in event_date_entries:
            event_entry= Event(
                event["event_id"],
                event["event_name"],
                EventType(event["event_type"]),
                event["game_title"],
                event["event_capacity"],
                date.fromisoformat(event["event_date"])
            )
            event_list.append(event_entry)

        return event_list
    
    finally:
        db_connection.close()
