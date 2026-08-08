"""Database connection setup file"""
import sqlite3
from pathlib import Path


def get_connection():
    """
    Open a connection to the cafe_league.db SQLite database file,
    configured and ready to use.

    Returns:
        sqlite3.Connection: an open connection with foreign key
        enforcement turned on and rows returned as sqlite3.Row
        objects (accessible by column name).
    """

    # Build an absolute path to cafe_league.db, based on where this
    # file (db.py) physically lives on disk — not on whatever folder
    # the terminal happens to be in when the program is run. This
    # guarantees the same database file is found every time,
    # regardless of the current working directory.
    db_path = Path(__file__).parent / "cafe_league.db"

    # Open (or create, if it doesn't exist yet) the SQLite database
    # file at db_path, and get back a Connection object representing
    # that open link to the file.
    connection = sqlite3.connect(db_path)

    # SQLite disables foreign key constraint enforcement by default,
    # and this setting is per-connection (it does NOT persist inside
    # the database file itself). Without this line, ON DELETE CASCADE
    # and other FK rules defined in schema.sql would silently be
    # ignored on this connection.
    connection.execute("PRAGMA foreign_keys = ON")

    # By default, query results come back as plain tuples, meaning
    # you'd have to access columns by position (row[0], row[1], ...).
    # Setting row_factory to sqlite3.Row lets you access columns by
    # name instead (row["player_name"]), which is far less fragile.
    connection.row_factory = sqlite3.Row

    # Hand the fully configured connection back to whatever called
    # this function, ready to run queries against.
    return connection
