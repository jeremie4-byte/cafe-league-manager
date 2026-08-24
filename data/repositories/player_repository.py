from data.db import get_connection
from datetime import datetime
from domains.player import Player, PlayerType

def save_player_entry(player_entry: Player):

    """We first establish the db connection """
    db_connection = get_connection()
    
    """We create the player_cursor to navigate and manipulate the player table"""
    player_cursor = db_connection.cursor()

    """We insert the player object using the .execute() method and the player_cursor"""

    """
    We try to do an INSERT STATEMENT WITH ALL SQL ATTRIBUTES.
    Then we add Values as (?, ?, ?, ?) since we are working with sqlite
    We then give the proper domain class fields to be entered
    """
    try: 
        player_cursor.execute("""
                INSERT INTO Cafe_Player (player_name, player_type, join_date, current_elo)
                VALUES (?,?, ?, ?)
                """,
                (
                    player_entry.player_name,
                    player_entry.player_type.value, # Gets the actual ENUM values from PlayerType that are accepted
                    player_entry.join_date.isoformat(), # No arguments are taken in an isoformat function it is a function that verifies, it does not transform
                    player_entry.current_elo,
                )
        )

        #We use the lastrowid functionality on the cursor to obtain the last generated ID from our player entry 
        new_player = player_cursor.lastrowid

        #Save changes
        db_connection.commit()
        print("Player entry, saved succesfully!")
        return new_player

    
    except Exception as e:
        #Undo changes if anything fails
        db_connection.rollback()
        print(f"Failed to insert player: {e}")
        raise #raise the exact error for the user

    #In both cases we close the db connection whether the insert was succesful or a failure. 
    finally:
        db_connection.close()

def get_player_by_id(player_id: int):

    """ We first establish the db connection """
    db_connection = get_connection()
    
    """ We create the player_cursor to navigate and manipulate the player table"""
    player_cursor = db_connection.cursor()

    """ 
    We find the matching data row with the ID.
    We must first use an SQL SELECT STATEMENT and add a 
    conditionnal WHERE clause
    """

    try:

        player_cursor.execute(
            """
            SELECT player_id, player_name, player_type, join_date, current_elo
            FROM Cafe_Player
            WHERE player_id = ?
            """,
            # A dictionnary of one element is expected and and so we put the element in (player_id,) with a trailing comma
            (player_id,)
        )

        # We fetch the one matching row
        player_row = player_cursor.fetchone()

        #We now extract our player object from the extracted row using an if statement to see that a row was found and not a None value
        if player_row is not None: 
            player_entry =Player(
                player_row["player_id"],#We write as a string to lookup the SQL column player_id NOT the function variable
                player_row["player_name"],
                PlayerType(player_row["player_type"]),
                datetime.fromisoformat(player_row["join_date"]), # We take the string and convert it back to a datetime format with the function fromisoformat()
                player_row["current_elo"]
            )
            return player_entry
        
        #If no corresponding player is found with the corresponding Id we raise a ValueError as the id is an invalid entry
        else:
            raise ValueError(f"No player found with player id {player_id}")
        
    finally:
        db_connection.close()

def delete_player_by_id(player_id: int):

    """ We first establish the db connection """
    db_connection = get_connection()
    
    """ We create the player_cursor to navigate and manipulate the player table"""
    player_cursor = db_connection.cursor()

    """ We try to delete the player entry using the ID"""
    try: 

        player_cursor.execute(
            """
            DELETE  FROM Cafe_Player 
            WHERE player_id = ?
            """,
            (player_id,)
        )

        """Row count allows us to see all entries with the inputed ID"""
        row_affected = player_cursor.rowcount

        """If none are found we raise a ValueError since there is nothing to delete"""
        if row_affected == 0:
            raise ValueError(f"No player found with player id {player_id}")
        
        #If one or more is found we delete the entries
        else:
            db_connection.commit()
            print("Player deleted succesfully!")
            return row_affected
        
    #Finally we close the db connection
    finally:
        db_connection.close()

def get_all_players():

    """We first establish the db connection"""
    db_connection = get_connection()

    """We create the player_cursor to naviguate and manipulate the player table"""
    player_cursor = db_connection.cursor()

    """ We now SELECT all player entries to display
        all player objects that have been created.
    """

    try:

        player_cursor.execute(
            """
            SELECT player_id, player_name, player_type, join_date, current_elo
            FROM Cafe_Player
            """
        )

        """ We assign a new variable (player_repository) where the cursor fetches all player entries"""

        player_repository = player_cursor.fetchall()

        """We create an empty list to append all player entries """
        player_list = []

        for player_row in player_repository:
            player_entry = Player(
                player_row["player_id"],
                player_row["player_name"],
                PlayerType(player_row["player_type"]),
                datetime.fromisoformat(player_row["join_date"]),
                player_row["current_elo"])
            player_list.append(player_entry)

        # We return all of the appended entries into the list
        return player_list

    #Close the db_connection when all the operations have been realised.
    finally:
        db_connection.close()
