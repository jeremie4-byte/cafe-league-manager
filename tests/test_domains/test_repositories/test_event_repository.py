import unittest
from unittest import mock
import os
import sqlite3
import tempfile
from pathlib import Path
from datetime import date

from services.validators import validate_event_date, validate_event_capacity
from domains.event import Event, EventType
from data.repositories.event_repository import save_event_entry, get_event_by_id, delete_event_by_id, get_all_events, update_event_attributes, get_event_by_name, get_event_by_type, get_event_by_game_title, get_event_by_capacity, get_event_by_date, get_upcoming_events, get_events_by_date_range, event_exists, get_next_event, get_past_events, search_events_by_name, count_events_by_type, get_busiest_game_titles, get_average_capacity

class TestEventRepository(unittest.TestCase):

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
            "data.repositories.event_repository.get_connection",
            side_effect= self.get_test_connection
        )
        self.patcher.start()

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

    def helper_event(
        self,
        event_id=1,
        event_name="Mario Kart Wii Grand Prix Championship",
        event_type=EventType.TOURNAMENT_MATCH,
        game_title="Mario Kart Wii",
        event_capacity=2,
        event_date=date(2026, 12, 12),
    ):
        return Event(event_id, event_name, event_type, game_title, event_capacity, event_date)
    
    def test_save_event(self):
        event = self.helper_event()
        saved_event= save_event_entry(event)
        valid_event = get_event_by_id(saved_event)
        self.assertEqual(1, valid_event.event_id)
        self.assertEqual("Mario Kart Wii Grand Prix Championship", valid_event.event_name)
        self.assertEqual(EventType.TOURNAMENT_MATCH, valid_event.event_type)
        self.assertEqual("Mario Kart Wii", valid_event.game_title)
        self.assertEqual(2, valid_event.event_capacity)
        self.assertEqual(date(2026, 12, 12), valid_event.event_date)

    def test_save_event_duplicate_id(self):
        original_event = self.helper_event()
        save_event_entry(original_event)
        duplicated_event = Event(
            1,
            "Mario Bros. Wii: Speedrun Bros.",
            EventType.RANKED_LEAGUE_MATCH,
            "New Super Mario Brothers Wii",
            50,
            date(2025, 3, 4)
        )
        with self.assertRaises(sqlite3.IntegrityError):
            save_event_entry(duplicated_event)

    def test_save_event_duplicate_name(self):
        original_event = self.helper_event()
        save_event_entry(original_event)
        duplicated_event = self.helper_event(event_id= 2)
        with self.assertRaises(sqlite3.IntegrityError):
            save_event_entry(duplicated_event)

    def test_save_all_event_types(self):
        event_1 = self.helper_event()
        event_2 = self.helper_event(event_id=2, 
                                    event_name="Super Samsh Bros Ultimate Championship",
                                    event_type= EventType.RANKED_LEAGUE_MATCH)
        event_3 = self.helper_event(event_id=3,
                                    event_name="Super Mario Galaxy: Good Egg Galaxy Speedrun Tutorial",
                                    event_type= EventType.OPEN_GAME_NIGHT)
        events = [event_1, event_2, event_3]
        for event in events:
            with self.subTest(event_type=event.event_type):
                saved_event = save_event_entry(event)
                fetched_event= get_event_by_id(saved_event)
                self.assertEqual(fetched_event.event_type, event.event_type)

    def test_get_event_by_missing_id(self):
        with self.assertRaises(ValueError):
            get_event_by_id(999)  
