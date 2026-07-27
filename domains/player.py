from enum import Enum
from datetime import datetime
from services.validators import *

"""Creating an Enum class for all different SQL player_type"""
class PlayerType(Enum):
    CASUAL_DROP_IN = "Casual Drop-In"
    LEAGUE_REGULAR = "League Regular"
    TOURNAMENT_COMPETITOR = "Tournament Competitor"

"""Creating Player class"""
class Player:
    def __init__(self, player_id, player_name, player_type: PlayerType, join_date: datetime, current_elo):
        self.player_id = validate_positive_id(player_id)
        self.player_name = validate_min_name_length(player_name)
        if not isinstance(player_type, PlayerType):
            raise TypeError("player_type must be a valid PlayerType enum instance")
        self.player_type = player_type
        self.join_date = validate_datetime_format(join_date)
        self.current_elo = validate_elo_range(current_elo)
