from enum import Enum
from datetime import datetime

"""Creating an Enum class for all different SQL player_type"""
class PlayerType(Enum):
    CASUAL_DROP_IN = "Casual Drop-In"
    LEAGUE_REGULAR = "League Regular"
    TOURNAMENT_COMPETITOR = "Tournament Competitor"

"""Creating Player class"""
class Player:
    def __init__(self, player_id, player_name, player_type: PlayerType, join_date: datetime, current_elo):
        self.player_id = player_id
        self.player_name = player_name
        self.player_type = player_type
        self.join_date = join_date
        self.current_elo = current_elo
