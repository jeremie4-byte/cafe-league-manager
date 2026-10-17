import unittest
from unittest import mock
import os
import sqlite3
import tempfile
from pathlib import Path
from datetime import datetime

from domains.player import Player, PlayerType
from data.repositories.player_repository import save_player_entry, get_player_by_id, delete_player_by_id, get_all_players, update_player_attributes, get_players_by_type, get_leaderboard, get_player_by_name

class TestPlayerRepository(unittest.TestCase):

    def setUp(self):
        self.file_descriptor, self.db_path = tempfile.mkstemp() # Close the raw file descriptor immediately so SQLite controls file access
        os.close(self.file_descriptor)

        schema_path = Path(__file__).parent.parent.parent / "data" / "schema.sql"

        with open(schema_path, "r") as schema_file: 
            schema_content = schema_file.read()
            
        schema_connection = sqlite3.connect(self.db_path)
        schema_connection.executescript(schema_content)
        schema_connection.commit()
        schema_connection.close()

        self.patcher = mock.patch(
            "data.repositories.player_repository.get_connection",
            side_effect=self.get_test_connection
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

    def test_save_player(self):
        player = Player(1, "Jeremie Lortie", PlayerType.CASUAL_DROP_IN, datetime(2020, 10, 22), 2000)
        saved_id = save_player_entry(player)
        self.assertIsNotNone(saved_id)

    def test_invalid_save_player(self):
        with self.assertRaises(Exception): # We run a method to make sure an invalid id will not be accepted
            player = Player("one", "Jacob Langlois", PlayerType.LEAGUE_REGULAR, datetime(2024, 4, 5), 1500)
            saved_id = save_player_entry(player)

    def test_negative_save_player(self):
        with self.assertRaises(Exception): 
            player = Player(-100, "Diana Dirtsaw", PlayerType.TOURNAMENT_COMPETITOR, datetime(2022, 6, 16), 3000)
            saved_id = save_player_entry(player)

    def test_zero_save_player_succeeds(self):
        player = Player(0, "Joan Martinez", PlayerType.CASUAL_DROP_IN, datetime(2024, 7, 30), 500)
        saved_id = save_player_entry(player)
        self.assertIsNotNone(saved_id)

    def test_get_player_by_id(self):
        player = Player(1, "Isabela Cruz", PlayerType.CASUAL_DROP_IN, datetime(2025, 9, 11), 1250)
        saved_id = save_player_entry(player) # We need to save the player in the database first so there is an existing
        fetched_player = get_player_by_id(saved_id) # Since the function expects a Player object we passed the made saved_id player object already made
        self.assertIsNotNone(fetched_player) # We first verify that the ID was actually generated and savec
        self.assertEqual(fetched_player.player_id, player.player_id) # We then verified that its the correcponsing ID of the Player object we created
        self.assertEqual(fetched_player.player_name, "Isabela Cruz") # We then verified that its the correcponsing name of the Player object we created

    def test_save_player_invalid_id(self):
        with self.assertRaises(ValueError):
            player = Player(-100, "Gustavo Fring", PlayerType.TOURNAMENT_COMPETITOR, datetime(2026, 6, 8), 2200)
            saved_id = save_player_entry(player)
            fetched_player = get_player_by_id(saved_id)

    def test_get_nonexistent_player_id (self): # Test to make sure an error raises when we try to fetch an ID of a player that doesn't exist
        with self.assertRaises(ValueError):
            fetched_player = get_player_by_id(999)

    def test_delete_player_by_id(self): #Test to make sure the delete function works properly
        # We first save a player
        player = Player(1, "George Champagne", PlayerType.LEAGUE_REGULAR, datetime(2015, 2, 6), 1800)
        saved_id = save_player_entry(player)

        # We then delete the player and check whether this evaluates as a True boolean (1)
        delete_result = delete_player_by_id(saved_id)
        self.assertTrue(delete_result)

        # We make sure the entry is gone from the database
        with self.assertRaises(ValueError):
            get_player_by_id(saved_id)
        

    def test_invalid_id_to_delete(self):
        with self.assertRaises(ValueError):
            invalid_player_id = delete_player_by_id(1000)

    def test_negative_id_to_delete(self): # Test to make sure negative ID arent deleted since they should raise a ValueError
        with self.assertRaises(ValueError):
            invalid_player_id_to_delete =  delete_player_by_id(-11)
    
    def test_0_id_to_delete(self): # Test to make sure that 0 is an invalid ID to delete as it should not exist
        with self.assertRaises(ValueError):
            zero_id = delete_player_by_id(0)

    def test_get_all_players(self): # test to make sure that wer can get the list of all players
        # We start by creating 3 player objects
        player1 = Player(1, "Leslie Falls", PlayerType.CASUAL_DROP_IN, datetime(2019, 8, 19), 2300)
        player2 = Player(2, "Jeannette Asturia", PlayerType.LEAGUE_REGULAR, datetime(2021, 1, 24), 3222)
        player3 = Player(3, "John Smith", PlayerType.TOURNAMENT_COMPETITOR, datetime(2023, 11, 12), 4000)

        # We then save all player entries using the save function
        saved_player_1 = save_player_entry(player1)
        saved_player_2 = save_player_entry(player2)
        saved_player_3 = save_player_entry(player3)

        # We then create an empty list and append all 3 entries
        player_list = []
        player_list.append(saved_player_1)
        player_list.append(saved_player_2)
        player_list.append(saved_player_3)

        # We now fetch all the player entries
        player_list = get_all_players()

        #We verify that the ID's were generated and saved
        self.assertIsNotNone(player_list)

        # We now verify that the player_list object attribute correspond to the original saved player object attributes
        self.assertEqual(player_list[0].player_id, player1.player_id)
        self.assertEqual(player_list[0].player_name, player1.player_name)
        self.assertEqual(player_list[0].player_type, player1.player_type)
        self.assertEqual(player_list[0].join_date, player1.join_date)
        self.assertEqual(player_list[0].current_elo, player1.current_elo)

        self.assertEqual(player_list[1].player_id, player2.player_id)
        self.assertEqual(player_list[1].player_name, player2.player_name)
        self.assertEqual(player_list[1].player_type, player2.player_type)
        self.assertEqual(player_list[1].join_date, player2.join_date)
        self.assertEqual(player_list[1].current_elo, player2.current_elo)

        self.assertEqual(player_list[2].player_id, player3.player_id)
        self.assertEqual(player_list[2].player_name, player3.player_name)
        self.assertEqual(player_list[2].player_type, player3.player_type)
        self.assertEqual(player_list[2].join_date, player3.join_date)
        self.assertEqual(player_list[2].current_elo, player3.current_elo)

    def test_get_all_players_empty(self): # Test to make sure an empty list is returned and not None
        player_list = get_all_players()
        self.assertIsNotNone(player_list) # We verify the list doesnt return None
        self.assertEqual(len(player_list), 0) # We make sure that an empty list gives back a length of 0 

    def test_update_player(self):
        # We start by building & saving a player object
        player = Player(1, "Brad Zelensky", PlayerType.LEAGUE_REGULAR, datetime(2025, 5, 16), 2700)
        saved_player = save_player_entry(player)

        # We now update the player attributes
        player.player_name = "John Barrymore"
        player.player_type = PlayerType.CASUAL_DROP_IN
        player.current_elo = 3000

        #We update the player
        fetched_player = update_player_attributes(saved_player, 
                                                  player.player_name, 
                                                  player.player_type, 
                                                  player.current_elo
                                                  )
        
        self.assertIsNotNone(fetched_player) # verify the update actually affected a row (rowcount isn't None) before checking the new values

        updated_player = get_player_by_id(saved_player) # We call the get function with saved-player as an argument to pull the new player object with updated info

        # We use assertEquals on updated_player to make sure the values match
        self.assertEqual(updated_player.player_name, "John Barrymore")
        self.assertEqual(updated_player.player_type, PlayerType.CASUAL_DROP_IN)
        self.assertEqual(updated_player.current_elo, 3000)

    def test_update_player_name(self):
         # We start by building & saving a player object
        player = Player(1, "Brad Zelensky", PlayerType.LEAGUE_REGULAR, datetime(2025, 5, 16), 2700)
        saved_player = save_player_entry(player)

        #We now only update the player name attribute
        player.player_name = "Drew Hoffman"

        # We update the player
        modified_player = update_player_attributes(
            saved_player,
            player.player_name
        )

        self.assertIsNotNone(modified_player) # verify the update actually affected a row (rowcount isn't None) before checking the new values

        updated_player = get_player_by_id(saved_player) # We call the get function with saved-player as an argument to pull the new player object with updated info

        # We use assertEqual to make sure the updated_player new value has been saved
        self.assertEqual(updated_player.player_name, "Drew Hoffman")

    def test_update_player_type(self):
         # We start by building & saving a player object
        player = Player(1, "Brad Zelensky", PlayerType.LEAGUE_REGULAR, datetime(2025, 5, 16), 2700)
        saved_player = save_player_entry(player)

        # We now only update the player type attribute
        player.player_type = PlayerType.TOURNAMENT_COMPETITOR

        # We update the player object
        modified_player = update_player_attributes(
            saved_player,
            player.player_name, 
            player.player_type
        )

        self.assertIsNotNone(modified_player) # verify the update actually affected a row (rowcount isn't None) before checking the new values

        updated_player = get_player_by_id(saved_player) # We call the get function with saved-player as an argument to pull the new player object with updated info

        # We use assertEqual to make sure the updated_player new value has been saved
        self.assertEqual(updated_player.player_type, PlayerType.TOURNAMENT_COMPETITOR)

    def test_update_current_elo(self):
        # We start by building & saving a player object
        player = Player(1, "Brad Zelensky", PlayerType.LEAGUE_REGULAR, datetime(2025, 5, 16), 2700)
        saved_player = save_player_entry(player)

        # We now only update the player elo attribute
        player.current_elo = 2500

        # We update the player object using the saved id and modified attribute
        modified_player = update_player_attributes(
            saved_player,
            player.player_name,
            player.player_type,
            player.current_elo
        )

        self.assertIsNotNone(modified_player) # verify the update actually affected a row (rowcount isn't None) before checking the new values

        # We call get_player_by_id on saved_player to get the new modified player object
        updated_player = get_player_by_id(saved_player)

        #We use assertEqual to make sure that the updated_player.current_elo attribute properly updated
        self.assertEqual(updated_player.current_elo, 2500)

    def test_invalid_update_player(self): # Test to raise exception when a player object isn't valid for an update
        with self.assertRaises(ValueError):
            player_id = 1
            player_name = "John Steinback"
            player_type = PlayerType.LEAGUE_REGULAR
            current_elo = 2450
            update_player_attributes(
                player_id,
                player_name,
                player_type,
                current_elo
            )

    def test_none_updated_attributes(self): # Test for an update when player_name, player_type and current_elo are left as None
        with self.assertRaises(ValueError):
            player_id = 1
            player_name = None
            player_type = None
            current_elo = None
            update_player_attributes(
                player_id,
                player_name,
                player_type,
                current_elo
            )

    def test_get_player_type_lists(self): #Test to make sure that the get_players_by_type function works and returns all CASUAL_DROP_IN players

        # We start by creating a bunch of players
        player1 = Player(1, "Alberta Ranchaw", PlayerType.CASUAL_DROP_IN, datetime(2020, 5, 20), 1000)
        player2 = Player(2, "Matthew McKnight", PlayerType.CASUAL_DROP_IN, datetime(2023, 3, 27), 550)
        player3 = Player(3, "Guillaume Deschamps", PlayerType.LEAGUE_REGULAR, datetime(2022, 2, 2), 3000)
        player4 = Player(4, "Benoit Trottier", PlayerType.LEAGUE_REGULAR, datetime(2025, 9, 10), 2200)
        player5 = Player(5, "Sasha Strasdong", PlayerType.TOURNAMENT_COMPETITOR, datetime(2024, 8, 18), 4000)
        player6 = Player(6, "Helen Carilla", PlayerType.TOURNAMENT_COMPETITOR, datetime(2026, 6, 30), 3700)

        # We must then save all players to afterwards call our function
        saved_player1 = save_player_entry(player1)
        saved_player2 = save_player_entry(player2)
        saved_player3 = save_player_entry(player3)
        saved_player4 = save_player_entry(player4)
        saved_player5 = save_player_entry(player5)
        saved_player6 = save_player_entry(player6)

        # We call get_players_by_type and assert the correct data and length for each player_type
        casual_drop_ins = get_players_by_type(PlayerType.CASUAL_DROP_IN)
        self.assertEqual(len(casual_drop_ins), 2)
        self.assertEqual(casual_drop_ins[0].player_name, "Alberta Ranchaw")
        self.assertEqual(casual_drop_ins[1].player_name, "Matthew McKnight")

        league_regulars = get_players_by_type(PlayerType.LEAGUE_REGULAR)
        self.assertEqual(len(league_regulars), 2)
        self.assertEqual(league_regulars[0].player_name, "Guillaume Deschamps")
        self.assertEqual(league_regulars[1].player_name, "Benoit Trottier")

        tournament_competitors = get_players_by_type(PlayerType.TOURNAMENT_COMPETITOR)
        self.assertEqual(len(tournament_competitors), 2)
        self.assertEqual(tournament_competitors[0].player_name, "Sasha Strasdong")
        self.assertEqual(tournament_competitors[1].player_name, "Helen Carilla")
        
    def test_get_leaderboard(self):

        #We create a list of Player objects with distinct elo scores
        player1 = Player(1, "Josee Lemieux", PlayerType.CASUAL_DROP_IN, datetime(2019, 12, 14), 4000)
        player2 = Player(2, "Pau Martinez", PlayerType.LEAGUE_REGULAR, datetime(2021, 7, 7), 3000)
        player3 = Player(3, "Andrea Rubina", PlayerType.TOURNAMENT_COMPETITOR, datetime(2024, 4, 29), 2000)
        player4 = Player(4, "Erica Stanst", PlayerType.CASUAL_DROP_IN, datetime(2020, 7, 18), 1000)

        # We must then save all players to afterwards call our function
        saved_player1 = save_player_entry(player1)
        saved_player2 = save_player_entry(player2)
        saved_player3 = save_player_entry(player3)
        saved_player4 = save_player_entry(player4)

        # We call our function and store it in the leaderboard_results variable
        leaderboard_results = get_leaderboard()

        # We use assertGreater to make sure the descending elo list was properly generated
        self.assertGreater(leaderboard_results[0].current_elo, leaderboard_results[1].current_elo)
        self.assertGreater(leaderboard_results[1].current_elo, leaderboard_results[2].current_elo)
        self.assertGreater(leaderboard_results[2].current_elo, leaderboard_results[3].current_elo)
        self.assertEqual(len(leaderboard_results), 4)

    def test_get_empty_leaderboard(self):
        player_list = get_leaderboard()
        self.assertIsNotNone(player_list) # We verify the list doesnt return None
        self.assertEqual(len(player_list), 0) # We make sure that an empty list gives back a length of 0 

    # Test to make sure that if two or more players have the same elo score that the one with lower id number is the first entry
    def test_tied_leaderboard(self): 

        #We create a list of Player objects with equal elo scores
        player1 = Player(1, "Andrew Dasgot", PlayerType.CASUAL_DROP_IN, datetime(2026, 9, 26), 2000)
        player2 = Player(2, "Iria Benllroch", PlayerType.LEAGUE_REGULAR, datetime(2025, 5, 15), 2000)

        # We must then save all players to afterwards call our function
        saved_player1 = save_player_entry(player1)
        saved_player2 = save_player_entry(player2)

        # We call our function and store it in the leaderboard_results variable
        leaderboard_results = get_leaderboard()

        # We verify that the first row is the object with player id 1 and the second one is 2
        self.assertEqual(leaderboard_results[0].player_id, 1)
        self.assertEqual(leaderboard_results[1].player_id, 2)

    # Test to make sure a valid case of get_player_by_name outputs properly
    def test_get_player_by_name(self):

        # We create a list of different players
        player1 = Player(1, "Mathias Ravento", PlayerType.CASUAL_DROP_IN, datetime(2022, 7, 12), 1000)
        player2 = Player(2, "Elena Oskta", PlayerType.LEAGUE_REGULAR, datetime(2023, 2, 28), 2000)
        player3 = Player(3, "Jason Derulo", PlayerType.TOURNAMENT_COMPETITOR, datetime(2017, 10, 16), 3000)

        # We must save all players and then we can call the get_player_by_name 
        saved_player1 = save_player_entry(player1)
        saved_player2 = save_player_entry(player2)
        saved_player3 = save_player_entry(player3)

        mathias_search = get_player_by_name("Mathias Ravento")
        self.assertEqual(mathias_search[0].player_name, "Mathias Ravento")

        elena_search = get_player_by_name("Elena Oskta")
        self.assertEqual(elena_search[0].player_name, "Elena Oskta")

        jason_search = get_player_by_name("Jason Derulo")
        self.assertEqual(jason_search[0].player_name, "Jason Derulo")

    #Test to make sure a nonexistent name does not return any entries
    def test_get_player_by_name_empty(self):
        nonexistant_name = get_player_by_name("John Doe")
        self.assertIsNotNone(nonexistant_name) # We make sure the list is generated and empty and that we dont have a None result
        self.assertEqual(len(nonexistant_name), 0) # We make sure the length of results of that list is 0

    def test_get_player_by_name_duplicate(self):

        # We create different player objects but with the same player_name attribute
        player1 = Player(1, "John Doe", PlayerType.CASUAL_DROP_IN, datetime(2019, 11, 21), 1000)
        player2 = Player(2, "John Doe", PlayerType.LEAGUE_REGULAR, datetime(2024, 8, 8), 2000)

        # We save all players and then call the get_player_by_name function
        saved_player1 = save_player_entry(player1)
        saved_player2 = save_player_entry(player2)

        john_doe_search = get_player_by_name("John Doe")
        self.assertEqual(john_doe_search[0].player_name, "John Doe")
        self.assertEqual(john_doe_search[1].player_name, "John Doe")
        self.assertEqual(len(john_doe_search), 2)
