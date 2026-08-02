from domains.player import Player, PlayerType
from domains.match_player import MatchPlayer, MatchResult, Attendance
from domains.event import EventType

K_FACTOR = 30

class EloCalculation:

    @staticmethod
    def probabilistic_elo(rating_a: float, rating_b: float) -> tuple[float, float]:
        if not (0 <= rating_a <= 4000) or not (0 <= rating_b <= 4000):
            raise ValueError("Ratings must be between 0 and 4000")
        win_prob_a = 1.0 / (1 + (10 ** ((rating_b - rating_a) / 400)))
        win_prob_b = 1.0 - win_prob_a
        return (win_prob_a, win_prob_b)
    
    @staticmethod
    def elo_outcome(players_list: list[Player],  match_players_list: list[MatchPlayer], event_type):

        if event_type == EventType.OPEN_GAME_NIGHT:
            return (players_list, {})

        # 1. Structural Guard Checks
        if len(players_list) != len(match_players_list):
            raise ValueError("Player list and MatchPlayer list must be the same length!")
        
        for player, match_player in zip(players_list, match_players_list):
            if player.player_id != match_player.player_id:
                raise ValueError(f"Mismatched player IDs: {player.player_id} vs {match_player.player_id}")

        # 2. Filter Active Players
        active_pairs = [
            (p, mp) for p, mp in zip(players_list, match_players_list)
            if mp.attendance == Attendance.ATTENDED
        ]

        if len(active_pairs) < 2:
            raise ValueError("At least 2 attended players are required to calculate Elo changes!")

        # 3. Calculate Elo Deltas
        elo_update = {}

        for player, match_player in active_pairs:
            rank_a = match_player.match_result.value[1]
            if rank_a is None:
                raise ValueError(f"Player {player.player_id} attended but has no valid match rank!")

            elo_delta = 0.0
            opponents_counted = 0

            for opponent, match_opponent in active_pairs:
                if player.player_id == opponent.player_id:
                    continue

                rank_b = match_opponent.match_result.value[1]
                if rank_b is None:
                    continue

                # Determine match score (1.0 for win, 0.5 for draw, 0.0 for loss)
                if rank_a < rank_b:
                    score = 1.0
                elif rank_a > rank_b:
                    score = 0.0
                else:
                    score = 0.5

                expected_score, _ = EloCalculation.probabilistic_elo(player.current_elo, opponent.current_elo)
                elo_delta += K_FACTOR * (score - expected_score)
                opponents_counted += 1

            if opponents_counted > 0:
                # Average delta across all opponents in multi-player match
                elo_update[player.player_id] = elo_delta / opponents_counted

        # 4. Apply Ratings Updates
        for player in players_list:
            if player.player_id in elo_update:
                new_rating = round(player.current_elo + elo_update[player.player_id])
                player.current_elo = max(0, min(new_rating, 4000))

        return (players_list, elo_update)
