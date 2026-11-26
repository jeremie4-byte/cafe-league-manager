import unittest
from unittest import mock
import os
import sqlite3
import tempfile
from pathlib import Path
from datetime import date, datetime

from domains.event import Event, EventType
from data.repositories.event_repository import (
    save_event_entry,
    get_event_by_id,
    delete_event_by_id,
    get_all_events,
    update_event_attributes,
    get_event_by_name,
    get_event_by_type,
    get_event_by_game_title,
    get_event_by_date,
    get_event_by_capacity,
    get_upcoming_events,
    get_events_by_date_range,
    event_exists,
    get_past_events,
    get_next_event,
    search_events_by_name
)
# Add these to the import list as you write tests for them:
# get_next_event, get_past_events, search_events_by_name,
# count_events_by_type, get_busiest_game_titles, get_average_capacity


class TestEventRepository(unittest.TestCase):

    # ------------------------------------------------------------------
    # Fixture and helpers
    # ------------------------------------------------------------------

    def setUp(self):
        # Close the raw file descriptor right away so SQLite controls the file
        self.file_descriptor, self.db_path = tempfile.mkstemp()
        os.close(self.file_descriptor)

        schema_path = Path(__file__).parent.parent.parent / "data" / "schema.sql"
        with open(schema_path, "r") as schema_file:
            schema_content = schema_file.read()

        schema_connection = sqlite3.connect(self.db_path)
        schema_connection.executescript(schema_content)
        schema_connection.commit()
        schema_connection.close()

        # Every repository function calls get_connection() itself, so redirect it to the temp db
        self.patcher = mock.patch(
            "data.repositories.event_repository.get_connection",
            side_effect=self.get_test_connection,
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
        """Builds an Event without saving it. event_id and event_name must be unique per saved event."""
        return Event(event_id, event_name, event_type, game_title, event_capacity, event_date)

    def save_events(self, *events):
        """Saves each event and returns the list of ids that save_event_entry gave back."""
        return [save_event_entry(event) for event in events]

    def names_of(self, events):
        """The set of event names in a list of events (order is ignored)."""
        return {event.event_name for event in events}

    # ------------------------------------------------------------------
    # save_event_entry
    # ------------------------------------------------------------------

    def test_save_event(self):
        event = self.helper_event()
        saved_id = save_event_entry(event)
        saved_event = get_event_by_id(saved_id)
        self.assertEqual(saved_event.event_id, 1)
        self.assertEqual(saved_event.event_name, event.event_name)
        self.assertEqual(saved_event.event_type, event.event_type)
        self.assertEqual(saved_event.game_title, event.game_title)
        self.assertEqual(saved_event.event_capacity, event.event_capacity)
        self.assertEqual(saved_event.event_date, event.event_date)

    def test_save_event_duplicate_id(self):
        self.save_events(self.helper_event())
        duplicated_event = self.helper_event(event_name="Speedrun Bros.")
        with self.assertRaises(sqlite3.IntegrityError):
            save_event_entry(duplicated_event)

    def test_save_event_duplicate_name(self):
        self.save_events(self.helper_event())
        duplicated_event = self.helper_event(event_id=2)
        with self.assertRaises(sqlite3.IntegrityError):
            save_event_entry(duplicated_event)

    def test_save_all_event_types(self):
        events = [
            self.helper_event(event_id=1, event_name="Tournament Night", event_type=EventType.TOURNAMENT_MATCH),
            self.helper_event(event_id=2, event_name="Ranked Night", event_type=EventType.RANKED_LEAGUE_MATCH),
            self.helper_event(event_id=3, event_name="Open Night", event_type=EventType.OPEN_GAME_NIGHT),
        ]
        for event in events:
            with self.subTest(event_type=event.event_type):
                saved_id = save_event_entry(event)
                self.assertEqual(get_event_by_id(saved_id).event_type, event.event_type)

    # ------------------------------------------------------------------
    # get_event_by_id and get_all_events
    # ------------------------------------------------------------------

    def test_get_event_by_missing_id(self):
        with self.assertRaises(ValueError):
            get_event_by_id(999)

    def test_get_all_events(self):
        events = [
            self.helper_event(event_id=1),
            self.helper_event(event_id=2, event_name="Super Mario Bros. 2 Championship"),
            self.helper_event(event_id=3, event_name="Super Mario Bros. 3 Championship"),
        ]
        self.save_events(*events)

        fetched_events = get_all_events()

        self.assertEqual(len(fetched_events), 3)
        self.assertEqual(self.names_of(fetched_events), self.names_of(events))

    def test_get_empty_events_list(self):
        fetched_events = get_all_events()
        self.assertIsNotNone(fetched_events)
        self.assertEqual(len(fetched_events), 0)

    # ------------------------------------------------------------------
    # delete_event_by_id
    # ------------------------------------------------------------------

    def test_delete_event_by_id(self):
        event_id = save_event_entry(self.helper_event())
        rows_deleted = delete_event_by_id(event_id)
        self.assertEqual(rows_deleted, 1)
        with self.assertRaises(ValueError):
            get_event_by_id(event_id)

    def test_delete_nonexistent_event_by_id(self):
        with self.assertRaises(ValueError):
            delete_event_by_id(999)

    def test_delete_same_id_twice(self):
        event_id = save_event_entry(self.helper_event())
        self.assertEqual(delete_event_by_id(event_id), 1)
        with self.assertRaises(ValueError):
            delete_event_by_id(event_id)

    def test_delete_only_removes_target_row(self):
        event_1 = self.helper_event(event_id=1)
        event_2 = self.helper_event(event_id=2, event_name="Super Mario Bros. 2 Championship")
        event_3 = self.helper_event(event_id=3, event_name="Super Mario Bros. 3 Championship")
        _, id_2, _ = self.save_events(event_1, event_2, event_3)

        delete_event_by_id(id_2)
        remaining = get_all_events()

        self.assertEqual(len(remaining), 2)
        self.assertEqual(self.names_of(remaining), {event_1.event_name, event_3.event_name})
        self.assertNotIn(event_2.event_name, self.names_of(remaining))

    # ------------------------------------------------------------------
    # update_event_attributes: success paths
    # ------------------------------------------------------------------

    def test_update_event_name(self):
        event = self.helper_event()
        saved_id = save_event_entry(event)
        new_name = "Mario Bros. 2 Championship"

        update_event_attributes(saved_id, event_name=new_name)

        updated_event = get_event_by_id(saved_id)
        self.assertNotEqual(updated_event.event_name, event.event_name)
        self.assertEqual(updated_event.event_name, new_name)
        self.assertEqual(updated_event.event_capacity, event.event_capacity)

    def test_update_event_type(self):
        event = self.helper_event()
        saved_id = save_event_entry(event)
        new_type = EventType.RANKED_LEAGUE_MATCH

        update_event_attributes(saved_id, event_type=new_type)

        updated_event = get_event_by_id(saved_id)
        self.assertNotEqual(updated_event.event_type, event.event_type)
        self.assertEqual(updated_event.event_type, new_type)
        self.assertEqual(updated_event.event_capacity, event.event_capacity)

    def test_update_game_title(self):
        event = self.helper_event()
        saved_id = save_event_entry(event)
        new_game_title = "Mario Kart CTGP"

        update_event_attributes(saved_id, game_title=new_game_title)

        updated_event = get_event_by_id(saved_id)
        self.assertNotEqual(updated_event.game_title, event.game_title)
        self.assertEqual(updated_event.game_title, new_game_title)
        self.assertEqual(updated_event.event_name, event.event_name)

    def test_update_event_capacity(self):
        event = self.helper_event()
        saved_id = save_event_entry(event)
        new_capacity = 4

        update_event_attributes(saved_id, event_capacity=new_capacity)

        updated_event = get_event_by_id(saved_id)
        self.assertNotEqual(updated_event.event_capacity, event.event_capacity)
        self.assertEqual(updated_event.event_capacity, new_capacity)
        self.assertEqual(updated_event.event_name, event.event_name)

    def test_update_event_date(self):
        event = self.helper_event()
        saved_id = save_event_entry(event)
        new_date = date(2026, 11, 11)

        update_event_attributes(saved_id, event_date=new_date)

        updated_event = get_event_by_id(saved_id)
        self.assertNotEqual(updated_event.event_date, event.event_date)
        self.assertEqual(updated_event.event_date, new_date)
        self.assertEqual(updated_event.event_capacity, event.event_capacity)

    def test_update_all_attributes(self):
        event = self.helper_event()
        saved_id = save_event_entry(event)

        update_event_attributes(
            saved_id,
            event_name="Super Mario Bros. Evening",
            event_type=EventType.OPEN_GAME_NIGHT,
            game_title="Super Mario Bros.",
            event_capacity=100,
            event_date=date(2026, 1, 1),
        )

        updated_event = get_event_by_id(saved_id)
        self.assertEqual(updated_event.event_name, "Super Mario Bros. Evening")
        self.assertEqual(updated_event.event_type, EventType.OPEN_GAME_NIGHT)
        self.assertEqual(updated_event.game_title, "Super Mario Bros.")
        self.assertEqual(updated_event.event_capacity, 100)
        self.assertEqual(updated_event.event_date, date(2026, 1, 1))

    def test_update_to_the_same_value(self):
        event = self.helper_event()
        saved_id = save_event_entry(event)

        rows_updated = update_event_attributes(saved_id, event_name=event.event_name)

        self.assertEqual(rows_updated, 1)
        self.assertEqual(get_event_by_id(saved_id).event_name, event.event_name)

    def test_update_event_only_changes_target_row(self):
        event_1 = self.helper_event(event_id=1)
        event_2 = self.helper_event(event_id=2, event_name="Super Mario Galaxy 2 Speedrun", event_capacity=4)
        event_3 = self.helper_event(event_id=3, event_name="Super Mario Galaxy Speedrun", event_capacity=4)
        id_1, id_2, id_3 = self.save_events(event_1, event_2, event_3)

        update_event_attributes(id_2, event_capacity=50)

        self.assertEqual(get_event_by_id(id_1).event_capacity, event_1.event_capacity)
        self.assertEqual(get_event_by_id(id_2).event_capacity, 50)
        self.assertEqual(get_event_by_id(id_3).event_capacity, event_3.event_capacity)

    # ------------------------------------------------------------------
    # update_event_attributes: failure paths
    # ------------------------------------------------------------------

    def test_update_event_no_fields(self):
        event = self.helper_event()
        saved_id = save_event_entry(event)

        with self.assertRaises(ValueError):
            update_event_attributes(saved_id)

        unchanged_event = get_event_by_id(saved_id)
        self.assertEqual(unchanged_event.event_name, event.event_name)
        self.assertEqual(unchanged_event.event_capacity, event.event_capacity)

    def test_update_event_missing_id(self):
        event = self.helper_event()
        saved_id = save_event_entry(event)

        with self.assertRaises(ValueError):
            update_event_attributes(999, event_name="The Legend of Zelda: Ocarina of Time")

        self.assertEqual(get_event_by_id(saved_id).event_name, event.event_name)

    def test_update_event_with_duplicate_name(self):
        event_1 = self.helper_event(event_id=1)
        event_2 = self.helper_event(event_id=2, event_name="Mario Kart Double Dash Grand Prix Championship")
        _, id_2 = self.save_events(event_1, event_2)

        with self.assertRaises(sqlite3.IntegrityError):
            update_event_attributes(id_2, event_name=event_1.event_name)

        self.assertEqual(get_event_by_id(id_2).event_name, event_2.event_name)

    def test_update_event_with_bad_capacity(self):
        event = self.helper_event()
        saved_id = save_event_entry(event)

        for bad_capacity in [-2, 0, 101]:
            with self.subTest(event_capacity=bad_capacity):
                with self.assertRaises(sqlite3.IntegrityError):
                    update_event_attributes(saved_id, event_capacity=bad_capacity)

        self.assertEqual(get_event_by_id(saved_id).event_capacity, event.event_capacity)

    def test_update_event_with_bad_date(self):
        event = self.helper_event()
        saved_id = save_event_entry(event)

        with self.assertRaises(TypeError):
            update_event_attributes(saved_id, event_date=datetime(2026, 10, 10))

        self.assertEqual(get_event_by_id(saved_id).event_date, event.event_date)

    # ------------------------------------------------------------------
    # get_event_by_name
    # ------------------------------------------------------------------

    def test_get_event_by_name(self):
        event_1 = self.helper_event(event_id=1)
        event_2 = self.helper_event(
            event_id=2,
            event_name="Super Mario Galaxy 2 Speedrun",
            game_title="Super Mario Galaxy 2",
            event_capacity=4,
            event_date=date(2025, 11, 17),
        )
        event_3 = self.helper_event(event_id=3, event_name="Super Mario Galaxy Speedrun")
        self.save_events(event_1, event_2, event_3)

        fetched_event = get_event_by_name(event_2.event_name)

        self.assertEqual(fetched_event.event_id, event_2.event_id)
        self.assertEqual(fetched_event.event_name, event_2.event_name)
        self.assertEqual(fetched_event.game_title, event_2.game_title)
        self.assertEqual(fetched_event.event_capacity, event_2.event_capacity)
        self.assertEqual(fetched_event.event_date, event_2.event_date)

    def test_get_event_by_missing_name(self):
        self.save_events(self.helper_event())
        with self.assertRaises(ValueError):
            get_event_by_name("Nonexistent Event")

    # ------------------------------------------------------------------
    # get_event_by_type
    # ------------------------------------------------------------------

    def test_get_event_by_type(self):
        event_1 = self.helper_event(event_id=1)  
        event_2 = self.helper_event(event_id=2, event_name="Galaxy 2 Speedrun", event_type=EventType.RANKED_LEAGUE_MATCH)
        event_3 = self.helper_event(event_id=3, event_name="Galaxy Speedrun", event_type=EventType.RANKED_LEAGUE_MATCH)
        self.save_events(event_1, event_2, event_3)

        fetched_events = get_event_by_type(EventType.RANKED_LEAGUE_MATCH)

        self.assertEqual(len(fetched_events), 2)
        self.assertEqual(self.names_of(fetched_events), {event_2.event_name, event_3.event_name})
        self.assertNotIn(event_1.event_name, self.names_of(fetched_events))

    def test_get_empty_event_type_list(self):
        self.save_events(
            self.helper_event(event_id=1),
            self.helper_event(event_id=2, event_name="Galaxy 2 Speedrun", event_type=EventType.RANKED_LEAGUE_MATCH),
        )

        fetched_events = get_event_by_type(EventType.OPEN_GAME_NIGHT)

        self.assertIsNotNone(fetched_events)
        self.assertEqual(len(fetched_events), 0)

    # ------------------------------------------------------------------
    # get_event_by_game_title
    # ------------------------------------------------------------------

    def test_get_events_by_game_title(self):
        event_1 = self.helper_event(event_id=1)
        event_2 = self.helper_event(event_id=2, event_name="Galaxy 2 Winter Speedrun", game_title="Super Mario Galaxy 2")
        event_3 = self.helper_event(event_id=3, event_name="Galaxy 2 Fall Speedrun", game_title="Super Mario Galaxy 2")
        self.save_events(event_1, event_2, event_3)

        fetched_events = get_event_by_game_title(event_2.game_title)

        self.assertEqual(len(fetched_events), 2)
        self.assertEqual(self.names_of(fetched_events), {event_2.event_name, event_3.event_name})
        self.assertNotIn(event_1.event_name, self.names_of(fetched_events))

    def test_get_empty_events_by_game_title(self):
        self.save_events(
            self.helper_event(event_id=1),
            self.helper_event(event_id=2, event_name="Galaxy 2 Speedrun", game_title="Super Mario Galaxy 2"),
        )

        fetched_events = get_event_by_game_title("New Super Mario Brothers")

        self.assertIsNotNone(fetched_events)
        self.assertEqual(len(fetched_events), 0)

    # ------------------------------------------------------------------
    # get_event_by_date
    # ------------------------------------------------------------------

    def test_get_events_by_date(self):
        event_1 = self.helper_event(event_id=1)  
        event_2 = self.helper_event(event_id=2, event_name="Galaxy 2 Speedrun", event_date=date(2025, 11, 17))
        event_3 = self.helper_event(event_id=3, event_name="Galaxy Speedrun", event_date=date(2025, 11, 17))
        self.save_events(event_1, event_2, event_3)

        fetched_events = get_event_by_date(event_2.event_date)

        self.assertEqual(len(fetched_events), 2)
        self.assertEqual(self.names_of(fetched_events), {event_2.event_name, event_3.event_name})
        self.assertNotIn(event_1.event_name, self.names_of(fetched_events))

    def test_get_empty_events_by_date_list(self):
        self.save_events(
            self.helper_event(event_id=1),
            self.helper_event(event_id=2, event_name="Galaxy 2 Speedrun", event_date=date(2025, 11, 17)),
        )

        fetched_events = get_event_by_date(date(2026, 11, 23))

        self.assertIsNotNone(fetched_events)
        self.assertEqual(len(fetched_events), 0)

    # ------------------------------------------------------------------
    # get_event_by_capacity
    # ------------------------------------------------------------------

    def save_capacity_events(self, top_capacity=100):
        """Four events with capacities 2, 4, 8 and top_capacity. Returns them in that order."""
        events = [
            self.helper_event(event_id=1, event_name="Capacity 2", event_capacity=2),
            self.helper_event(event_id=2, event_name="Capacity 4", event_capacity=4),
            self.helper_event(event_id=3, event_name="Capacity 8", event_capacity=8),
            self.helper_event(event_id=4, event_name="Capacity Top", event_capacity=top_capacity),
        ]
        self.save_events(*events)
        return events

    def test_get_event_by_capacity(self):
        event_1, event_2, event_3, event_4 = self.save_capacity_events()

        fetched_events = get_event_by_capacity(min_capacity=4, max_capacity=8)

        self.assertEqual(len(fetched_events), 2)
        self.assertEqual(self.names_of(fetched_events), {event_2.event_name, event_3.event_name})
        self.assertNotIn(event_1.event_name, self.names_of(fetched_events))
        self.assertNotIn(event_4.event_name, self.names_of(fetched_events))

    def test_get_event_with_missing_max_value_capacity(self):
        event_1, event_2, event_3, event_4 = self.save_capacity_events()

        fetched_events = get_event_by_capacity(min_capacity=8, max_capacity=None)

        self.assertEqual(len(fetched_events), 2)
        self.assertEqual(self.names_of(fetched_events), {event_3.event_name, event_4.event_name})

    def test_get_event_with_missing_min_value_capacity(self):
        event_1, event_2, event_3, event_4 = self.save_capacity_events()

        fetched_events = get_event_by_capacity(min_capacity=None, max_capacity=7)

        self.assertEqual(len(fetched_events), 2)
        self.assertEqual(self.names_of(fetched_events), {event_1.event_name, event_2.event_name})

    def test_get_event_by_not_in_range_capacity(self):
        self.save_capacity_events(top_capacity=75)  

        fetched_events = get_event_by_capacity(76, 100)

        self.assertIsNotNone(fetched_events)
        self.assertEqual(len(fetched_events), 0)

    def test_get_event_by_no_bounds_capacity(self):
        self.save_capacity_events()
        with self.assertRaises(ValueError):
            get_event_by_capacity(min_capacity=None, max_capacity=None)

    def test_get_event_with_bigger_min_than_max_capacity(self):
        self.save_capacity_events()
        with self.assertRaises(ValueError):
            get_event_by_capacity(min_capacity=100, max_capacity=10)

    # ------------------------------------------------------------------
    # event_exists
    # ------------------------------------------------------------------

    def test_event_exists(self):
        event_1 = self.helper_event(event_id=1)
        event_2 = self.helper_event(event_id=2, event_name="Galaxy 2 Winter Speedrun")
        self.save_events(event_1, event_2)

        self.assertIs(event_exists(event_2.event_name), True)

    def test_event_exists_missing_name(self):
        self.save_events(
            self.helper_event(event_id=1),
            self.helper_event(event_id=2, event_name="Galaxy 2 Winter Speedrun"),
        )

        self.assertIs(event_exists("New Super Mario Brothers"), False)

    def test_event_exists_empty_table(self):
        self.assertIs(event_exists("Super Mario Galaxy"), False)

    # ------------------------------------------------------------------
    # get_upcoming_events
    # ------------------------------------------------------------------

    def test_get_upcoming_events(self):
        event_1 = self.helper_event(event_id=1)  # 2026-12-12
        event_2 = self.helper_event(event_id=2, event_name="Winter Speedrun", event_date=date(2025, 11, 17))
        event_3 = self.helper_event(event_id=3, event_name="Fall Speedrun", event_date=date(2027, 1, 22))
        event_4 = self.helper_event(event_id=4, event_name="Cocktail Night", event_date=date(2027, 1, 15))
        self.save_events(event_1, event_2, event_3, event_4)

        fetched_events = get_upcoming_events(event_date=date(2026, 11, 25))

        self.assertEqual(len(fetched_events), 3)
        names = [event.event_name for event in fetched_events]  # a list, because order matters here
        self.assertEqual(names, [event_1.event_name, event_4.event_name, event_3.event_name])
        self.assertNotIn(event_2.event_name, names)

    def test_get_empty_upcoming_events(self):
        self.save_events(
            self.helper_event(event_id=1, event_date=date(2025, 12, 12)),
            self.helper_event(event_id=2, event_name="Winter Speedrun", event_date=date(2025, 11, 17)),
            self.helper_event(event_id=3, event_name="Fall Speedrun", event_date=date(2025, 1, 22)),
        )

        fetched_events = get_upcoming_events(event_date=date(2026, 11, 25))

        self.assertIsNotNone(fetched_events)
        self.assertEqual(len(fetched_events), 0)

    def test_get_upcoming_event_inclusive_boundary(self):
        event_1 = self.helper_event(event_id=1)
        event_2 = self.helper_event(event_id=2, event_name="Winter Speedrun", event_date=date(2025, 11, 17))
        event_3 = self.helper_event(event_id=3, event_name="Fall Speedrun", event_date=date(2027, 1, 22))
        event_4 = self.helper_event(event_id=4, event_name="Cocktail Night", event_date=date(2027, 3, 15))
        self.save_events(event_1, event_2, event_3, event_4)

        # Event 4 is the only one on or after its own date, so >= (not >) is what keeps it in
        fetched_events = get_upcoming_events(event_date=event_4.event_date)

        self.assertEqual(len(fetched_events), 1)
        self.assertEqual(self.names_of(fetched_events), {event_4.event_name})

    def test_get_upcoming_events_no_date_parameter(self):
        # 2000 and 2099 are far enough apart that today's date always falls between them
        event_1 = self.helper_event(event_id=1, event_date=date(2000, 2, 12))
        event_2 = self.helper_event(event_id=2, event_name="Winter Speedrun", event_date=date(2099, 11, 17))
        self.save_events(event_1, event_2)

        fetched_events = get_upcoming_events()

        self.assertIsNotNone(fetched_events)
        self.assertEqual(len(fetched_events), 1)
        self.assertEqual(self.names_of(fetched_events), {event_2.event_name})

    # ------------------------------------------------------------------
    # get_events_by_date_range
    # ------------------------------------------------------------------

    def test_get_events_by_date_range(self):
        event_1 = self.helper_event(event_id=1)  # 2026-12-12
        event_2 = self.helper_event(event_id=2, event_name="Winter Speedrun", event_date=date(2025, 11, 17))
        event_3 = self.helper_event(event_id=3, event_name="Fall Speedrun", event_date=date(2027, 1, 22))
        event_4 = self.helper_event(event_id=4, event_name="Cocktail Night", event_date=date(2027, 1, 15))
        event_5 = self.helper_event(event_id=5, event_name="Partners in Time Night", event_date=date(2028, 3, 3))
        self.save_events(event_1, event_2, event_3, event_4, event_5)

        # Events 2 and 3 sit exactly on the bounds, so this also proves the bounds are inclusive
        fetched_events = get_events_by_date_range(event_2.event_date, event_3.event_date)

        self.assertIsNotNone(fetched_events)
        self.assertEqual(len(fetched_events), 4)
        names = [event.event_name for event in fetched_events]  # a list, because the result is sorted by date
        self.assertEqual(names, [event_2.event_name, event_1.event_name, event_4.event_name, event_3.event_name])
        self.assertNotIn(event_5.event_name, names)

    def test_get_events_by_date_range_start_only(self):
        event_1 = self.helper_event(event_id=1)  # 2026-12-12
        event_2 = self.helper_event(event_id=2, event_name="Winter Speedrun", event_date=date(2025, 11, 17))
        event_3 = self.helper_event(event_id=3, event_name="Fall Speedrun", event_date=date(2027, 1, 22))
        event_4 = self.helper_event(event_id=4, event_name="Cocktail Night", event_date=date(2027, 1, 15))
        self.save_events(event_1, event_2, event_3, event_4)

        fetched_events = get_events_by_date_range(start_date=event_1.event_date)

        self.assertIsNotNone(fetched_events)
        names = [event.event_name for event in fetched_events]
        self.assertEqual(names, [event_1.event_name, event_4.event_name, event_3.event_name])
        self.assertNotIn(event_2.event_name, names)

    def test_get_events_by_date_range_end_only(self):
        event_1= self.helper_event(event_id=1)
        event_2= self.helper_event(event_id=2, event_name="Winter Speedrun", event_date=date(2025, 11, 17))
        event_3= self.helper_event(event_id=3, event_name="Fall Speedrun", event_date=date(2027, 1, 22))
        event_4= self.helper_event(event_id=4, event_name="Cocktail Night", event_date=date(2027, 1, 15))
        self.save_events(event_1, event_2, event_3, event_4)

        fetched_events= get_events_by_date_range(end_date=event_1.event_date)

        self.assertIsNotNone(fetched_events)
        names = [event.event_name for event in fetched_events]
        self.assertEqual(names, [event_2.event_name, event_1.event_name])
        self.assertNotIn(event_3.event_name, names)
        self.assertNotIn(event_4.event_name, names)

    def test_get_events_by_date_range_no_results(self):
        event_1= self.helper_event(event_id=1)
        event_2= self.helper_event(event_id=2, event_name="Winter Speedrun", event_date=date(2025, 11, 17))
        event_3= self.helper_event(event_id=3, event_name="Fall Speedrun", event_date=date(2027, 1, 22))
        event_4= self.helper_event(event_id=4, event_name="Cocktail Night", event_date=date(2027, 1, 15))
        self.save_events(event_1, event_2, event_3, event_4)

        fetched_events= get_events_by_date_range(start_date=date(2028, 1, 1), end_date=date(2028, 12, 31))

        self.assertIsNotNone(fetched_events)
        self.assertEqual(len(fetched_events), 0)

    def test_get_events_by_inverted_date_range(self):
        event_1= self.helper_event(event_id=1)
        event_2= self.helper_event(event_id=2, event_name="Winter Speedrun", event_date=date(2025, 11, 17))
        event_3= self.helper_event(event_id=3, event_name="Fall Speedrun", event_date=date(2027, 1, 22))
        event_4= self.helper_event(event_id=4, event_name="Cocktail Night", event_date=date(2027, 1, 15))
        self.save_events(event_1, event_2, event_3, event_4)

        with self.assertRaises(ValueError):
            get_events_by_date_range(start_date=event_3.event_date, end_date=event_2.event_date)

    def test_get_events_without_date_range(self):
        event_1= self.helper_event(event_id=1)
        event_2= self.helper_event(event_id=2, event_name="Winter Speedrun", event_date=date(2025, 11, 17))
        event_3= self.helper_event(event_id=3, event_name="Fall Speedrun", event_date=date(2027, 1, 22))
        event_4= self.helper_event(event_id=4, event_name="Cocktail Night", event_date=date(2027, 1, 15))
        self.save_events(event_1, event_2, event_3, event_4)

        with self.assertRaises(ValueError):
            get_events_by_date_range()

    def test_get_events_by_datetime_range(self):
        event_1= self.helper_event(event_id=1)
        event_2= self.helper_event(event_id=2, event_name="Winter Speedrun", event_date=date(2025, 11, 17))
        event_3= self.helper_event(event_id=3, event_name="Fall Speedrun", event_date=date(2027, 1, 22))
        event_4= self.helper_event(event_id=4, event_name="Cocktail Night", event_date=date(2027, 1, 15))
        self.save_events(event_1, event_2, event_3, event_4)

        with self.assertRaises(TypeError):
            get_events_by_date_range(start_date=event_1.event_date, end_date=datetime(2026, 11, 11))

    # ------------------------------------------------------------------
    # get_past_events
    # ------------------------------------------------------------------

    def test_get_past_events(self):
        event_1= self.helper_event(event_id=1)
        event_2= self.helper_event(event_id=2, event_name="Winter Speedrun", event_date=date(2025, 11, 17))
        event_3= self.helper_event(event_id=3, event_name="Fall Speedrun", event_date=date(2027, 1, 22))
        event_4= self.helper_event(event_id=4, event_name="Cocktail Night", event_date=date(2027, 1, 15))
        self.save_events(event_1, event_2, event_3, event_4)

        fetched_events= get_past_events(event_4.event_date) # returns only event 2 and event 1 as it is everything prior to event_4 date

        self.assertIsNotNone(fetched_events)
        self.assertEqual(len(fetched_events), 2)
        names = [event.event_name for event in fetched_events]
        self.assertEqual(names, [event_1.event_name, event_2.event_name])
        self.assertNotIn(event_3.event_name, names)
        self.assertNotIn(event_4.event_name, names)

    def test_get_no_parameter_past_events(self):
        event_1= self.helper_event(event_id=1)
        event_2= self.helper_event(event_id=2, event_name="Winter Speedrun", event_date=date(2025, 11, 17))
        event_3= self.helper_event(event_id=3, event_name="Fall Speedrun", event_date=date(2027, 1, 22))
        event_4= self.helper_event(event_id=4, event_name="Cocktail Night", event_date=date(2027, 1, 15))
        self.save_events(event_1, event_2, event_3, event_4)

        fetched_events= get_past_events()

        self.assertIsNotNone(fetched_events)
        self.assertEqual(len(fetched_events), 1)
        names= [event.event_name for event in fetched_events]
        self.assertEqual(names, [event_2.event_name])
        self.assertNotIn(event_1.event_name, names)
        self.assertNotIn(event_3.event_name, names)
        self.assertNotIn(event_4.event_name, names)

    def test_get_same_date_past_events(self):
        event_1= self.helper_event(event_id=1)
        event_2= self.helper_event(event_id=2, event_name="Winter Speedrun", event_date=date(2026, 12, 12))
        event_3= self.helper_event(event_id=3, event_name="Fall Speedrun", event_date=date(2027, 1, 22))
        event_4= self.helper_event(event_id=4, event_name="Cocktail Night", event_date=date(2027, 1, 15))
        self.save_events(event_2, event_1, event_3, event_4)

        fetched_events= get_past_events(event_4.event_date) # returns only event 2 and event 1 as it is everything prior to event_4 date

        self.assertIsNotNone(fetched_events)
        self.assertEqual(len(fetched_events), 2)
        names = [event.event_name for event in fetched_events]
        self.assertEqual(names, [event_1.event_name, event_2.event_name])
        self.assertNotIn(event_3.event_name, names)
        self.assertNotIn(event_4.event_name, names)

    # ------------------------------------------------------------------
    # get_next_events
    # ------------------------------------------------------------------

    def test_get_next_event(self):
        event_1= self.helper_event(event_id=1)
        event_2= self.helper_event(event_id=2, event_name="Winter Speedrun", event_date=date(2025, 11, 17))
        event_3= self.helper_event(event_id=3, event_name="Fall Speedrun", event_date=date(2027, 1, 22))
        event_4= self.helper_event(event_id=4, event_name="Cocktail Night", event_date=date(2027, 1, 15))
        self.save_events(event_2, event_1, event_3, event_4)

        fetched_event= get_next_event(from_date=event_1.event_date)
        self.assertEqual(fetched_event.event_id, 4)
        self.assertEqual(fetched_event.event_name, "Cocktail Night")

    def test_get_next_event_no_date(self):
        event_1= self.helper_event(event_id=1, event_date= date(2099, 12, 12))
        event_2= self.helper_event(event_id=2, event_name="Winter Speedrun", event_date=date(2000, 11, 17))
        self.save_events(event_1, event_2)

        fetched_event= get_next_event()
        self.assertEqual(fetched_event.event_id, 1)
        self.assertEqual(fetched_event.event_name, "Mario Kart Wii Grand Prix Championship")

    def test_get_no_future_next_event(self):
        event_1= self.helper_event(event_id=1)
        event_2= self.helper_event(event_id=2, event_name="Winter Speedrun", event_date=date(2026, 12, 12))
        self.save_events(event_1, event_2)

        fetched_event= get_next_event(from_date=event_1.event_date)
        self.assertIsNone(fetched_event)

    # ------------------------------------------------------------------
    # search_events_by_name()
    # ------------------------------------------------------------------






# TODO (later): get_past_events, get_next_event, search_events_by_name, aggregates


if __name__ == "__main__":
    unittest.main()
