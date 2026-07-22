from domains.event import Event, EventType
import unittest
from datetime import datetime
from enum import Enum

class TestEvent(unittest.TestCase):

    """Default set up case for testing"""
    def setUp(self):
        self.event = Event(1, "Brothers in Mario Bros", "Open Game Night", "Mario Bros", 50, datetime(2026, 7, 22))

    """Default event test case for event"""
    def test_default_case(self):
        self.assertEqual(self.event.event_id, 1)
        self.assertEqual(self.event.event_name, "Brothers in Mario Bros")
        self.assertEqual(self.event.event_type, "Open Game Night")
        self.assertEqual(self.event.game_title, "Mario Bros")
        self.assertEqual(self.event.event_capacity, 50)
        self.assertEqual(self.event.event_date, datetime(2026, 7, 22))

    """Test invalid event_id below 1"""
    def test_invalid_event_id(self):
        with self.assertRaises(ValueError):
            event2 = Event(-5, "Chaining Links", "Ranked League Match", "The Legend of Zelda: Ocarina of Time", 20, datetime(2026, 6, 20))

    """Test valid 1 ID"""
    def test_valid_1event_id(self):
        event3 = Event(1, "Bombless Bomber Man", "Tournament Match", "Bomberman", 35, datetime(2025, 12, 12))
        self.assertEqual(event3.event_id, 1)

    """Test valid event ID"""
    def test_valid_event_id(self):
        event4 = Event(2, "Pokemon Red: Nuzlock", "Ranked League Match", "Pokemon: Red Edition", 15, datetime(2026, 1, 5))
        self.assertEqual(event4.event_id, 2)

    """Test invalid event name"""
    def test_invalid_event_name(self):
        with self.assertRaises(ValueError):
            event5 = Event(3, "", "Open Game Night", "Mario Bros", 23, datetime(2026, 2, 27))

    """Test valid event name"""
    def test_valid_event_name(self):
        event6 = Event(4, "BLJ sequence break", "Ranked League Match", "Mario 64", 20, datetime(2025, 11, 11))
        self.assertEqual(event6.event_name, "BLJ sequence break")

    """Test valid Open Game Night event type"""
    def test_open_game_night(self):
        event7 = Event(5, "Labrador Nintendogs Caretakers", "Open Game Night", "Nintendogs", 50, datetime(2026, 3, 30))
        self.assertEqual(event7.event_type, "Open Game Night")

    """Test valid Ranked League Match event type"""
    def test_ranked_league_match(self):
        event8 = Event(6, "Super Samsh Bros Ultimate Finals", "Ranked League Match", "Super Smash Bros Ultimate", 2, datetime(2024, 10, 9))
        self.assertEqual(event8.event_type, "Ranked League Match")

    """Test valid Tournament Match"""
    def test_tournament_match(self):
        event9 = Event(7, "Mortal Komabt 3: Quarter Finals", "Tournament Match", "Mortal Kombat 3", 8, datetime(2026, 5, 22))

    """Test invalid event type"""
    def test_invalid_event_type(self):
        with self.assertRaises(ValueError):
            event10 = Event(8, "MW2: Terminal No-Scopes", "Free-for-all", "Call of Duty: Modern Warfare 2", 16, datetime(2026, 4, 23))

    """Test invalid Game Title"""
    def test_invalid_game_title(self):
        with self.assertRaises(ValueError):
            event11 = Event(9, "Ascension Zombies Tournament", "Open Game Night", "", 75, datetime(2025, 8, 17))
    
    """Test valid Game Title"""
    def test_valid_game_title(self):
        event12 = Event(10, "Plants vs zombies: TDM", "Tournament Match", "Plants vs. Zombies", 80, datetime(2025, 5, 4))
        self.assertEqual(event12.game_title, "Plants vs. Zombies")

    """Test invalid event date format"""
    def test_invalid_event_date(self):
        with self.assertRaises(ValueError):
            event13 = Event(11, "Minecraft: speedrun of the ender Dragon Quest", "Ranked League Match", "Minecraft", 100, "2026-07-09")

    """Test valid event date format"""
    def test_valid_event_date(self):
        event14 = Event(12, "Grand Theft Auto V: Hide and Seek", "Open Game Night", "Grand Theft Auto V", 90, datetime(2026, 6, 11))
        self.assertEqual(event14.event_date, datetime(2026, 6, 11))

    """Test 1 game capacity"""
    def test_1_game_capacity(self):
        event15 = Event(13, "Mario Kart Mushroom Gorge: Shroomless", "Tournament Match", "Mario Kart Wii", 1, datetime(2025, 11, 14))
        self.assertEqual(event15.event_capacity, 1)

    """Test 100 game capacity"""
    def test_100_game_capacity(self):
        event16 = Event(14, "Mario Kart Night", "Open Game Night", "Mario Kart", 100, datetime(2024, 1, 24))
        self.assertEqual(event16.event_capacity, 100)

    """Test invalid game capacity"""
    def test_invalid_game_capacity(self):
        with self.assertRaises(ValueError):
            event17 = Event(15, "Pac-Man 99 Speedrun", "Ranked League Match", "Pac-Man", -200, datetime(2026, 4, 25))

    """Test valid game capacity"""
    def test_valid_game_capacity(self):
        event18 = Event(16, "Fortnite: TDM", "Tournament Match", "Fortnite", 65, datetime(2024, 9, 19))
        self.assertEqual(event18.event_capacity, 65)
