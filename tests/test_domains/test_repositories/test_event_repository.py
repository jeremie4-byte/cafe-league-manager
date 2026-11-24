import unittest
from unittest import mock
import os
import sqlite3
import tempfile
from pathlib import Path
from datetime import date, datetime

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

    def test_get_all_events(self):
        event_1 = self.helper_event()
        event_2 = self.helper_event(
            event_id= 2,
            event_name= "Super Mario Bros. 2 Championship",
            game_title= "Super Mario Bros. 2"
        ) 
        event_3 = self.helper_event(
            event_id= 3,
            event_name= "Super Mario Bros. 3 Championship",
            game_title= "Super Mario Bros. 3"
        )
        saved_event_1 = save_event_entry(event_1)
        saved_event_2 = save_event_entry(event_2)
        saved_event_3 = save_event_entry(event_3)
        fetched_events = get_all_events()
        self.assertEqual(len(fetched_events), 3)
        events = [event_1, event_2, event_3]
        names = set()
        for event in fetched_events:
            names.add(event.event_name)
        for fetched_event in events:
            with self.subTest(fetched_event.event_name):
                self.assertIn(fetched_event.event_name, names)

    def test_get_empty_events_list(self):
        fetched_events = get_all_events()
        self.assertIsNotNone(fetched_events)
        self.assertEqual(len(fetched_events), 0)

    def test_delete_event_by_id(self):
        event = self.helper_event()
        event_id = save_event_entry(event)
        deleted_event = delete_event_by_id(event_id)
        self.assertTrue(deleted_event)
        with self.assertRaises(ValueError):
            get_event_by_id(event_id)

    def test_delete_nonexistant_event_by_id(self):
        with self.assertRaises(ValueError):
            delete_event_by_id(999)

    def test_delete_middle_list_event(self):
        event_1 = self.helper_event()
        event_2 = self.helper_event(
            event_id= 2,
            event_name= "Super Mario Bros. 2 Championship",
            game_title= "Super Mario Bros. 2"
        ) 
        event_3 = self.helper_event(
            event_id= 3,
            event_name= "Super Mario Bros. 3 Championship",
            game_title= "Super Mario Bros. 3"
        )
        save_event_entry(event_1)
        saved_event_2 = save_event_entry(event_2)
        save_event_entry(event_3)
        delete_event_by_id(saved_event_2)
        fetched_events = get_all_events()
        self.assertEqual(len(fetched_events), 2)
        names = set()
        for fetched_event in fetched_events:
            names.add(fetched_event.event_name)
        self.assertEqual(names, {event_1.event_name, event_3.event_name})
        self.assertNotIn(event_2.event_name, names)

    def test_delete_same_id(self):
        event = self.helper_event()
        event_id = save_event_entry(event)
        rows_deleted = delete_event_by_id(event_id)
        self.assertEqual(rows_deleted, 1)
        with self.assertRaises(ValueError):
            delete_event_by_id(event_id)

    def test_update_event_name(self):
        event= self.helper_event()
        saved_event= save_event_entry(event)
        new_name = "Mario Bros. 2 Championship"
        update_event_attributes(saved_event, 
                                new_name
                            )
        updated_event = get_event_by_id(saved_event)
        self.assertNotEqual(updated_event.event_name, event.event_name)
        self.assertEqual(updated_event.event_name, new_name)
        self.assertEqual(updated_event.event_capacity, event.event_capacity)

    def test_update_event_type(self):
        event= self.helper_event()
        saved_event= save_event_entry(event)
        new_event_type= EventType.RANKED_LEAGUE_MATCH
        update_event_attributes(
            saved_event,
            event_type= new_event_type
        )
        updated_event= get_event_by_id(saved_event)
        self.assertNotEqual(event.event_type, updated_event.event_type)
        self.assertEqual(updated_event.event_type, new_event_type)
        self.assertEqual(event.event_capacity, updated_event.event_capacity)

    def test_update_game_title(self):
        event= self.helper_event()
        saved_event= save_event_entry(event)
        new_game_title= "Mario Kart CTGP"
        update_event_attributes( saved_event,
                                 game_title= new_game_title
                                )
        updated_event= get_event_by_id(saved_event)
        self.assertNotEqual(event.game_title, updated_event.game_title)
        self.assertEqual(updated_event.game_title, new_game_title)
        self.assertEqual(updated_event.event_capacity, event.event_capacity)

    def test_update_event_capacity(self):
        event= self.helper_event()
        saved_event= save_event_entry(event)
        new_event_capacity = 4
        update_event_attributes(
            saved_event,
            event_capacity= new_event_capacity
        )
        updated_event= get_event_by_id(saved_event)
        self.assertNotEqual(event.event_capacity, updated_event.event_capacity)
        self.assertEqual(updated_event.event_capacity, new_event_capacity)
        self.assertEqual(event.event_name, updated_event.event_name)

    def test_update_event_date(self):
        event= self.helper_event()
        saved_event= save_event_entry(event)
        new_event_date= date(2026, 11, 11)
        update_event_attributes(
            saved_event,
            event_date= new_event_date
        )
        updated_event = get_event_by_id(saved_event)
        self.assertNotEqual(event.event_date, updated_event.event_date)
        self.assertEqual(updated_event.event_date, new_event_date)
        self.assertEqual(event.event_capacity, updated_event.event_capacity)

    def test_update_all_attributes(self):
        event= self.helper_event()
        saved_event= save_event_entry(event)
        new_event_name = "Super Mario Bros. Evening"
        new_event_type = EventType.OPEN_GAME_NIGHT
        new_game_title= "Super Mario Bros."
        new_event_capacity= 100
        new_event_date = date(2026, 1, 1)
        update_event_attributes(
            saved_event,
            event_name= new_event_name,
            event_type= new_event_type,
            game_title= new_game_title,
            event_capacity= new_event_capacity,
            event_date= new_event_date
        )
        updated_event= get_event_by_id(saved_event)
        self.assertNotEqual(event.event_name, updated_event.event_name)
        self.assertEqual(updated_event.event_name, new_event_name)
        self.assertEqual(updated_event.event_type, new_event_type)
        self.assertEqual(updated_event.game_title, new_game_title)
        self.assertEqual(updated_event.event_capacity, new_event_capacity)
        self.assertEqual(updated_event.event_date, new_event_date)

    def test_update_event_no_fields(self):
        event = self.helper_event()
        saved_event= save_event_entry(event)
        with self.assertRaises(ValueError):
            update_event_attributes(saved_event)
        unchanged_event= get_event_by_id(saved_event)
        self.assertEqual(unchanged_event.event_name, event.event_name)
        self.assertEqual(unchanged_event.event_capacity, event.event_capacity)


    def test_update_event_missing_id(self):
        event = self.helper_event()
        saved_event = save_event_entry(event)
        with self.assertRaises(ValueError):
            update_event_attributes(999, event_name="The Legend of Zelda: Ocarina of Time")
        unchanged_event = get_event_by_id(saved_event)
        self.assertEqual(unchanged_event.event_name, event.event_name)

    def test_update_event_with_duplicate_name(self):
        event_1= self.helper_event()
        event_2= Event(
            event_id= 2,
            event_name="Mario Kart Double Dash Grand Prix Championship",
            event_type=EventType.TOURNAMENT_MATCH,
            game_title="Mario Kart Wii",
            event_capacity=2,
            event_date=date(2026, 12, 12),
        )
        saved_event_1 = save_event_entry(event_1)
        saved_event_2 = save_event_entry(event_2)
        with self.assertRaises(sqlite3.IntegrityError):
            update_event_attributes(
                saved_event_2,
                event_name= event_1.event_name
            )
        unchanged_event= get_event_by_id(saved_event_2)
        self.assertEqual(unchanged_event.event_name, event_2.event_name)

    def test_update_event_with_bad_capacity(self):
        event_1= self.helper_event()
        event_2= Event(
            event_id= 2,
            event_name="Mario Kart Double Dash Grand Prix Championship",
            event_type=EventType.TOURNAMENT_MATCH,
            game_title="Mario Kart Wii",
            event_capacity=2,
            event_date=date(2026, 12, 12),
        )
        saved_event_1 = save_event_entry(event_1)
        saved_event_2 = save_event_entry(event_2)
        with self.assertRaises(sqlite3.IntegrityError):
            update_event_attributes(
                saved_event_2,
                event_capacity= -2
            )
        with self.assertRaises(sqlite3.IntegrityError):
            update_event_attributes(
                saved_event_2,
                event_capacity= 101
            )
        with self.assertRaises(sqlite3.IntegrityError):
            update_event_attributes(
                saved_event_2,
                event_capacity= 0
            )
        unchanged_event= get_event_by_id(saved_event_2)
        self.assertEqual(unchanged_event.event_capacity, event_2.event_capacity)

    def test_update_event_with_bad_date(self):
        event_1= self.helper_event()
        event_2= Event(
            event_id= 2,
            event_name="Mario Kart Double Dash Grand Prix Championship",
            event_type=EventType.TOURNAMENT_MATCH,
            game_title="Mario Kart Wii",
            event_capacity=2,
            event_date=date(2026, 12, 12),
        )
        saved_event_1 = save_event_entry(event_1)
        saved_event_2 = save_event_entry(event_2)
        with self.assertRaises(TypeError):
            update_event_attributes(
                saved_event_2,
                event_date= datetime(2026, 10, 10)
            )
        unchanged_event= get_event_by_id(saved_event_2)
        self.assertEqual(unchanged_event.event_date, event_2.event_date)

    def test_update_to_the_same_value(self):
        event= self.helper_event()
        saved_event= save_event_entry(event)
        update_event_attributes(
            saved_event,
            event_name= "Mario Kart Wii Grand Prix Championship"
        )
        unchanged_event= get_event_by_id(saved_event)
        self.assertEqual(unchanged_event.event_name, event.event_name)

    def test_update_event_only_changes_target_row(self):
        event_1 = self.helper_event()
        event_2 = Event(
            event_id= 2,
            event_name= "Super Mario Galaxy 2 Speedrun",
            event_type= EventType.RANKED_LEAGUE_MATCH,
            game_title= "Super Mario Galaxy 2",
            event_capacity= 4,
            event_date= date(2025, 11, 17)
        )
        event_3 = Event(
            event_id= 3,
            event_name= "Super Mario Galaxy Speedrun",
            event_type= EventType.RANKED_LEAGUE_MATCH,
            game_title= "Super Mario Galaxy",
            event_capacity= 4,
            event_date= date(2026, 1, 22)
        )
        saved_event_1= save_event_entry(event_1)
        saved_event_2= save_event_entry(event_2)
        saved_event_3= save_event_entry(event_3)
        update_event_attributes(
            saved_event_2,
            event_capacity= 50
        )
        unchanged_event_1= get_event_by_id(saved_event_1)
        changed_event_2= get_event_by_id(saved_event_2)
        unchanged_event_3= get_event_by_id(saved_event_3)
        self.assertEqual(unchanged_event_1.event_capacity, event_1.event_capacity)
        self.assertEqual(changed_event_2.event_capacity, 50)
        self.assertEqual(unchanged_event_3.event_capacity, event_3.event_capacity)

    def test_get_event_by_name(self):
        event_1= self.helper_event()
        event_2 = Event(
            event_id= 2,
            event_name= "Super Mario Galaxy 2 Speedrun",
            event_type= EventType.RANKED_LEAGUE_MATCH,
            game_title= "Super Mario Galaxy 2",
            event_capacity= 4,
            event_date= date(2025, 11, 17)
        )
        event_3 = Event(
            event_id= 3,
            event_name= "Super Mario Galaxy Speedrun",
            event_type= EventType.RANKED_LEAGUE_MATCH,
            game_title= "Super Mario Galaxy",
            event_capacity= 4,
            event_date= date(2026, 1, 22)
        )
        saved_event_1= save_event_entry(event_1)
        saved_event_2= save_event_entry(event_2)
        saved_event_3= save_event_entry(event_3)
        fetched_event= get_event_by_name(event_2.event_name)
        self.assertEqual(event_2.event_id, fetched_event.event_id)
        self.assertEqual(event_2.event_name, fetched_event.event_name)
        self.assertEqual(event_2.game_title, fetched_event.game_title)
        self.assertEqual(event_2.event_capacity, fetched_event.event_capacity)
        self.assertEqual(event_2.event_date, fetched_event.event_date)

    def test_get_event_by_missing_name(self):
        event= self.helper_event()
        save_event_entry(event)
        with self.assertRaises(ValueError):
            get_event_by_name("Non Existant Event")

    def test_get_event_by_type(self):
        event_1= self.helper_event()
        event_2 = Event(
            event_id= 2,
            event_name= "Super Mario Galaxy 2 Speedrun",
            event_type= EventType.RANKED_LEAGUE_MATCH,
            game_title= "Super Mario Galaxy 2",
            event_capacity= 4,
            event_date= date(2025, 11, 17)
        )
        event_3 = Event(
            event_id= 3,
            event_name= "Super Mario Galaxy Speedrun",
            event_type= EventType.RANKED_LEAGUE_MATCH,
            game_title= "Super Mario Galaxy",
            event_capacity= 4,
            event_date= date(2026, 1, 22)
        )
        saved_event_1= save_event_entry(event_1)
        saved_event_2= save_event_entry(event_2)
        saved_event_3= save_event_entry(event_3)
        fetched_events = get_event_by_type(EventType.RANKED_LEAGUE_MATCH)
        self.assertEqual(len(fetched_events), 2)
        names= set()
        for fetched_event in fetched_events:
            names.add(fetched_event.event_name)
        self.assertNotIn(event_1.event_name, names)
        events= [event_2, event_3]
        for event in events:
            with self.subTest(event_name=event.event_name):
                self.assertIn(event.event_name, names)

    def test_get_empty_event_type_list(self):
        event_1= self.helper_event()
        event_2 = Event(
            event_id= 2,
            event_name= "Super Mario Galaxy 2 Speedrun",
            event_type= EventType.RANKED_LEAGUE_MATCH,
            game_title= "Super Mario Galaxy 2",
            event_capacity= 4,
            event_date= date(2025, 11, 17)
        )
        event_3 = Event(
            event_id= 3,
            event_name= "Super Mario Galaxy Speedrun",
            event_type= EventType.RANKED_LEAGUE_MATCH,
            game_title= "Super Mario Galaxy",
            event_capacity= 4,
            event_date= date(2026, 1, 22)
        )
        saved_event_1= save_event_entry(event_1)
        saved_event_2= save_event_entry(event_2)
        saved_event_3= save_event_entry(event_3)
        fetched_events= get_event_by_type(EventType.OPEN_GAME_NIGHT)
        self.assertIsNotNone(fetched_events)
        self.assertEqual(len(fetched_events), 0)

    def test_get_events_by_game_title(self):
        event_1= self.helper_event()
        event_2 = Event(
            event_id= 2,
            event_name= "Super Mario Galaxy 2 Winter Speedrun",
            event_type= EventType.RANKED_LEAGUE_MATCH,
            game_title= "Super Mario Galaxy 2",
            event_capacity= 4,
            event_date= date(2025, 11, 17)
        )
        event_3 = Event(
            event_id= 3,
            event_name= "Super Mario Galaxy 2 Fall Speedrun",
            event_type= EventType.RANKED_LEAGUE_MATCH,
            game_title= "Super Mario Galaxy 2",
            event_capacity= 4,
            event_date= date(2026, 1, 22)
        )
        saved_event_1= save_event_entry(event_1)
        saved_event_2= save_event_entry(event_2)
        saved_event_3= save_event_entry(event_3)
        fetched_events= get_event_by_game_title(event_2.game_title)
        self.assertEqual(len(fetched_events), 2)
        names= set()
        for fetched_event in fetched_events:
            names.add(fetched_event.event_name)
        self.assertNotIn(event_1.event_name, names)
        events= [event_2, event_3]
        for event in events:
            with self.subTest(event_name=event.event_name):
                self.assertIn(event.event_name, names)

    def test_get_empty_events_by_game_title(self):
        event_1= self.helper_event()
        event_2 = Event(
            event_id= 2,
            event_name= "Super Mario Galaxy 2 Speedrun",
            event_type= EventType.RANKED_LEAGUE_MATCH,
            game_title= "Super Mario Galaxy 2",
            event_capacity= 4,
            event_date= date(2025, 11, 17)
        )
        event_3 = Event(
            event_id= 3,
            event_name= "Super Mario Galaxy Speedrun",
            event_type= EventType.RANKED_LEAGUE_MATCH,
            game_title= "Super Mario Galaxy",
            event_capacity= 4,
            event_date= date(2026, 1, 22)
        )
        saved_event_1= save_event_entry(event_1)
        saved_event_2= save_event_entry(event_2)
        saved_event_3= save_event_entry(event_3)
        fetched_events= get_event_by_game_title("New Super Mario Borthers")
        self.assertIsNotNone(fetched_events)
        self.assertEqual(len(fetched_events), 0)

    def test_get_events_by_date(self):
        event_1= self.helper_event()
        event_2 = Event(
            event_id= 2,
            event_name= "Super Mario Galaxy 2 Speedrun",
            event_type= EventType.RANKED_LEAGUE_MATCH,
            game_title= "Super Mario Galaxy 2",
            event_capacity= 4,
            event_date= date(2025, 11, 17)
        )
        event_3 = Event(
            event_id= 3,
            event_name= "Super Mario Galaxy Speedrun",
            event_type= EventType.RANKED_LEAGUE_MATCH,
            game_title= "Super Mario Galaxy",
            event_capacity= 4,
            event_date= date(2025, 11, 17)
        )
        saved_event_1= save_event_entry(event_1)
        saved_event_2= save_event_entry(event_2)
        saved_event_3= save_event_entry(event_3)
        fetched_events= get_event_by_date(event_2.event_date)
        self.assertEqual(len(fetched_events), 2)
        names= set()
        for fetched_event in fetched_events:
            names.add(fetched_event.event_name)
        self.assertNotIn(event_1.event_name, names)
        events= [event_2, event_3]
        for event in events:
            with self.subTest(event_name=event.event_name):
                self.assertIn(event.event_name, names)

    def test_get_empty_events_by_date_list(self):
        event_1= self.helper_event()
        event_2 = Event(
            event_id= 2,
            event_name= "Super Mario Galaxy 2 Winter Speedrun",
            event_type= EventType.RANKED_LEAGUE_MATCH,
            game_title= "Super Mario Galaxy 2",
            event_capacity= 4,
            event_date= date(2025, 11, 17)
        )
        event_3 = Event(
            event_id= 3,
            event_name= "Super Mario Galaxy 2 Fall Speedrun",
            event_type= EventType.RANKED_LEAGUE_MATCH,
            game_title= "Super Mario Galaxy 2",
            event_capacity= 4,
            event_date= date(2026, 1, 22)
        )
        saved_event_1= save_event_entry(event_1)
        saved_event_2= save_event_entry(event_2)
        saved_event_3= save_event_entry(event_3)
        fetched_events= get_event_by_date(date(2026, 11, 23))
        self.assertIsNotNone(fetched_events)
        self.assertEqual(len(fetched_events), 0)

    def test_get_event_by_capacity(self):
        event_1= self.helper_event()
        event_2 = Event(
            event_id= 2,
            event_name= "Super Mario Galaxy 2 Winter Speedrun",
            event_type= EventType.RANKED_LEAGUE_MATCH,
            game_title= "Super Mario Galaxy 2",
            event_capacity= 4,
            event_date= date(2025, 11, 17)
        )
        event_3 = Event(
            event_id= 3,
            event_name= "Super Mario Galaxy 2 Fall Speedrun",
            event_type= EventType.RANKED_LEAGUE_MATCH,
            game_title= "Super Mario Galaxy 2",
            event_capacity= 8,
            event_date= date(2026, 1, 22)
        )
        event_4= Event(
            event_id= 4,
            event_name= "Super Mario Party Jamboree Cocktail Night",
            event_type= EventType.OPEN_GAME_NIGHT,
            game_title= "Super Mario Party Jamboree",
            event_capacity= 100,
            event_date= date(2027, 1, 15)
        )
        saved_event_1= save_event_entry(event_1)
        saved_event_2= save_event_entry(event_2)
        saved_event_3= save_event_entry(event_3)
        saved_event_4= save_event_entry(event_4)
        fetched_events= get_event_by_capacity(min_capacity= 4, max_capacity=8)
        self.assertEqual(len(fetched_events), 2)
        names= set()
        for fetched_event in fetched_events:
            names.add(fetched_event.event_name)
        self.assertNotIn(event_1.event_name, names)
        self.assertNotIn(event_4.event_name, names)
        events= [event_2, event_3]
        for event in events:
            with self.subTest(event_name= event.event_name):
                self.assertIn(event.event_name, names)

    def test_get_event_with_missing_max_value_capacity(self):
        event_1= self.helper_event()
        event_2 = Event(
            event_id= 2,
            event_name= "Super Mario Galaxy 2 Winter Speedrun",
            event_type= EventType.RANKED_LEAGUE_MATCH,
            game_title= "Super Mario Galaxy 2",
            event_capacity= 4,
            event_date= date(2025, 11, 17)
        )
        event_3 = Event(
            event_id= 3,
            event_name= "Super Mario Galaxy 2 Fall Speedrun",
            event_type= EventType.RANKED_LEAGUE_MATCH,
            game_title= "Super Mario Galaxy 2",
            event_capacity= 8,
            event_date= date(2026, 1, 22)
        )
        event_4= Event(
            event_id= 4,
            event_name= "Super Mario Party Jamboree Cocktail Night",
            event_type= EventType.OPEN_GAME_NIGHT,
            game_title= "Super Mario Party Jamboree",
            event_capacity= 100,
            event_date= date(2027, 1, 15)
        )
        saved_event_1= save_event_entry(event_1)
        saved_event_2= save_event_entry(event_2)
        saved_event_3= save_event_entry(event_3)
        saved_event_4= save_event_entry(event_4)
        fetched_events= get_event_by_capacity(min_capacity= 8, max_capacity= None)
        self.assertEqual(len(fetched_events), 2)
        names = set()
        for fetched_event in fetched_events:
            names.add(fetched_event.event_name)
        self.assertNotIn(event_1.event_name, names)
        self.assertNotIn(event_2.event_name, names)
        events= [event_3, event_4]
        for event in events:
            with self.subTest(event_name= event.event_name):
                self.assertIn(event.event_name, names)

    def test_get_event_with_missing_min_value_capacity(self):
        event_1= self.helper_event()
        event_2 = Event(
            event_id= 2,
            event_name= "Super Mario Galaxy 2 Winter Speedrun",
            event_type= EventType.RANKED_LEAGUE_MATCH,
            game_title= "Super Mario Galaxy 2",
            event_capacity= 4,
            event_date= date(2025, 11, 17)
        )
        event_3 = Event(
            event_id= 3,
            event_name= "Super Mario Galaxy 2 Fall Speedrun",
            event_type= EventType.RANKED_LEAGUE_MATCH,
            game_title= "Super Mario Galaxy 2",
            event_capacity= 8,
            event_date= date(2026, 1, 22)
        )
        event_4= Event(
            event_id= 4,
            event_name= "Super Mario Party Jamboree Cocktail Night",
            event_type= EventType.OPEN_GAME_NIGHT,
            game_title= "Super Mario Party Jamboree",
            event_capacity= 100,
            event_date= date(2027, 1, 15)
        )
        saved_event_1= save_event_entry(event_1)
        saved_event_2= save_event_entry(event_2)
        saved_event_3= save_event_entry(event_3)
        saved_event_4= save_event_entry(event_4)
        fetched_events= get_event_by_capacity(min_capacity=None, max_capacity=7)
        self.assertEqual(len(fetched_events), 2)
        names= set()
        for fetched_event in fetched_events:
            names.add(fetched_event.event_name)
        self.assertNotIn(event_3.event_name, names)
        self.assertNotIn(event_4.event_name, names)
        events= [event_1, event_2]
        for event in events:
            with self.subTest(event_name= event.event_name):
                self.assertIn(event.event_name, names)

    def test_get_event_by_not_in_range_capacity(self):
        event_1= self.helper_event()
        event_2 = Event(
            event_id= 2,
            event_name= "Super Mario Galaxy 2 Winter Speedrun",
            event_type= EventType.RANKED_LEAGUE_MATCH,
            game_title= "Super Mario Galaxy 2",
            event_capacity= 4,
            event_date= date(2025, 11, 17)
        )
        event_3 = Event(
            event_id= 3,
            event_name= "Super Mario Galaxy 2 Fall Speedrun",
            event_type= EventType.RANKED_LEAGUE_MATCH,
            game_title= "Super Mario Galaxy 2",
            event_capacity= 8,
            event_date= date(2026, 1, 22)
        )
        event_4= Event(
            event_id= 4,
            event_name= "Super Mario Party Jamboree Cocktail Night",
            event_type= EventType.OPEN_GAME_NIGHT,
            game_title= "Super Mario Party Jamboree",
            event_capacity= 75,
            event_date= date(2027, 1, 15)
        )
        fetched_events= get_event_by_capacity(76, 100)
        self.assertIsNotNone(fetched_events)
        self.assertEqual(len(fetched_events), 0)

    def test_get_event_by_no_bounds_capacity(self):
        event_1= self.helper_event()
        event_2 = Event(
            event_id= 2,
            event_name= "Super Mario Galaxy 2 Winter Speedrun",
            event_type= EventType.RANKED_LEAGUE_MATCH,
            game_title= "Super Mario Galaxy 2",
            event_capacity= 4,
            event_date= date(2025, 11, 17)
        )
        event_3 = Event(
            event_id= 3,
            event_name= "Super Mario Galaxy 2 Fall Speedrun",
            event_type= EventType.RANKED_LEAGUE_MATCH,
            game_title= "Super Mario Galaxy 2",
            event_capacity= 8,
            event_date= date(2026, 1, 22)
        )
        event_4= Event(
            event_id= 4,
            event_name= "Super Mario Party Jamboree Cocktail Night",
            event_type= EventType.OPEN_GAME_NIGHT,
            game_title= "Super Mario Party Jamboree",
            event_capacity= 75,
            event_date= date(2027, 1, 15)
        )
        saved_event_1= save_event_entry(event_1)
        saved_event_2= save_event_entry(event_2)
        saved_event_3= save_event_entry(event_3)
        saved_event_4= save_event_entry(event_4)
        with self.assertRaises(ValueError):
            fetched_events= get_event_by_capacity(min_capacity= None, max_capacity= None)

    def test_get_event_with_bigger_min_than_max_capacity(self):
        event_1= self.helper_event()
        event_2 = Event(
            event_id= 2,
            event_name= "Super Mario Galaxy 2 Winter Speedrun",
            event_type= EventType.RANKED_LEAGUE_MATCH,
            game_title= "Super Mario Galaxy 2",
            event_capacity= 4,
            event_date= date(2025, 11, 17)
        )
        event_3 = Event(
            event_id= 3,
            event_name= "Super Mario Galaxy 2 Fall Speedrun",
            event_type= EventType.RANKED_LEAGUE_MATCH,
            game_title= "Super Mario Galaxy 2",
            event_capacity= 8,
            event_date= date(2026, 1, 22)
        )
        event_4= Event(
            event_id= 4,
            event_name= "Super Mario Party Jamboree Cocktail Night",
            event_type= EventType.OPEN_GAME_NIGHT,
            game_title= "Super Mario Party Jamboree",
            event_capacity= 75,
            event_date= date(2027, 1, 15)
        )
        saved_event_1= save_event_entry(event_1)
        saved_event_2= save_event_entry(event_2)
        saved_event_3= save_event_entry(event_3)
        saved_event_4= save_event_entry(event_4)
        with self.assertRaises(ValueError):
            fetched_events= get_event_by_capacity(min_capacity=100, max_capacity= 10)

    def test_event_exists(self):
        event_1= self.helper_event()
        event_2 = Event(
            event_id= 2,
            event_name= "Super Mario Galaxy 2 Winter Speedrun",
            event_type= EventType.RANKED_LEAGUE_MATCH,
            game_title= "Super Mario Galaxy 2",
            event_capacity= 4,
            event_date= date(2025, 11, 17)
        )
        saved_event_1= save_event_entry(event_1)
        saved_event_2= save_event_entry(event_2)
        result= event_exists(event_2.event_name)
        self.assertIs(result, True)

    def test_event_exists_missing_name(self):
        event_1= self.helper_event()
        event_2 = Event(
            event_id= 2,
            event_name= "Super Mario Galaxy 2 Winter Speedrun",
            event_type= EventType.RANKED_LEAGUE_MATCH,
            game_title= "Super Mario Galaxy 2",
            event_capacity= 4,
            event_date= date(2025, 11, 17)
        )
        saved_event_1= save_event_entry(event_1)
        saved_event_2= save_event_entry(event_2)
        result= event_exists("New Super Mario Brothers")
        self.assertIs(result, False)

    def test_unsaved_event_exists(self):
        result=event_exists("Super Mario Galaxy")
        self.assertIs(result, False)
