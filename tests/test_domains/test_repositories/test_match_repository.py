import unittest
from unittest import mock
import os
import sqlite3
import tempfile
from pathlib import Path
from datetime import datetime

from domains.match import Match
from domains.event import Event, EventType
from data.repositories.match_repository import save_match_entry, get_match_by_id, delete_match_by_id, get_all_matches, get_match_by_event_id, get_all_matches_by_time

class TestMatchRepository(unittest.TestCase):

    def setUp(self):
        self.file_descriptor, self.db_path = tempfile.mkstemp() # Close the raw file descriptor immediately so SQLite controls file access
        os.close(self.file_descriptor)

        schema_path = Path(__file__).parent.parent.parent / "data" / "schema.sql"

        with open (schema_path, "r") as schema_file:
            schema_content = schema_file.read()

        schema_connection = sqlite3.connect(self.db_path)
        schema_connection.executescript(schema_content)
        schema_connection.commit()
        schema_connection.close()

        self.patcher = mock.patch(
            "data.repositories.match_repository.get_connection",
            side_effect= self.get_test_connection
        )
        self.patcher.start()

        event = Event( 1, "Mario Bros 3 Speedrun", EventType.RANKED_LEAGUE_MATCH, "Super Mario Brothers 3", 50, datetime(2020, 10, 10))
        # before testing the match repository you need to create the event repository as its a foreign key in this table

    def get_test_connection(self):
        connection = sqlite3.connect(self.db_path)
        connection.execute("PRAGMA foreign_keys = ON")
        connection.row_factory = sqlite3.Row
        return connection 

    def tearDown(self):
        try:
            self.patcher.stop()
        finally:
            if os.path.exists(self.db_path):
                os.remove(self.db_path)

    def test_save_match(self):
        match = Match(1, 1 , datetime(2020, 10, 10))
        saved_match = save_match_entry(match)
        self.assertIsNotNone(saved_match)

    def test_save_invalid_match(self):
        with self.assertRaises(Exception):
            match = Match("1", 1, datetime(2020, 10, 10))
            match_2 = Match(-1, 1, datetime(2020, 10, 10))
            saved_match = save_match_entry(match)
            saved_match2 = save_match_entry(match_2)

    def test_save_zero_match(self):
        match = Match(0, 1, datetime(2020, 10, 10))
        saved_match = save_match_entry(match)
        self.assertIsNotNone(saved_match)

    def test_get_match_by_id(self):
        match = Match(1, 1, datetime(2020, 10, 10))
        saved_match = save_match_entry(match)
        fetched_match = get_match_by_id(saved_match)
        self.assertIsNotNone(fetched_match)
        self.assertEqual(fetched_match.event_id, match.event_id)
        self.assertEqual(fetched_match.schedule_match_time, match.schedule_match_time)
