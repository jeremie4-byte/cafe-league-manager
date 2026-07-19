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
        if player_type != "Casual Drop-In" and player_type != "League Regular" and player_type != "Tournament Competitor":
            raise ValueError
        self.join_date = join_date
        # We verify that join_date was actually entered as datetime format, if not we raise a value error
        if not isinstance(join_date, datetime):
            raise ValueError
        self.current_elo = current_elo
        if current_elo < 0 or current_elo > 4000:
            raise ValueError
