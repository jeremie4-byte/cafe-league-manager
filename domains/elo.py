from player import Player
from match_player import MatchPlayer, MatchResult, Attendance
K_FACTOR = 30

class EloCalculation:
    #We start by calculating the player's win probability
    @staticmethod
    def probabilistic_elo(rating_a, rating_b):
        win_probabilityA =1.0 / (1 + (10**((rating_b - rating_a)/400)))
        win_probabilityB = 1 - win_probabilityA
        return (win_probabilityA, win_probabilityB)
    
    #Static method to calculate duel win, draw and loses elo
    @staticmethod
    def elo_outcome(players_list, match_players_list):
        #We make a new list conssiting of players and all the players within the specific match
        player_ranking = list(zip(players_list, match_players_list))

        #Match variables for winning, drawing or losing, which will be used later to update player elo
        MATCH_WIN = 1.0
        MATCH_DRAW = 0.5
        MATCH_LOSE = 0.0
        
        #empty dictionnary to store elo changes
        elo_update = {}
        #The outerloop examines a current player
        for player, match_player in player_ranking:

            #if condition verifying attendance, if a player cancelled or didn't show up, the algorithm skips them entirely
            if match_player.attendance == Attendance.CANCELLED or match_player.attendance == Attendance.NO_SHOW:
                continue
            
            #Elo changes to be stored in elo_data and to be applied after all possible matchups of inner loop
            elo_delta = 0

            # Counter used to count total number of opposing players to modify K_FACTOR distributions
            counter = 0

            #Inner loop to check scores against all other opponents for the current player
            for opponent, match_opponent in player_ranking:
                #If the player is the same as the opponent, we don't calculate their elo score and move on to compare the results with the next opponent
                if player == opponent:
                    continue
                
                # If the opponent cancelled or did not show up, skip the elo calculation and move on to the next
                elif match_opponent.attendance == Attendance.CANCELLED or match_opponent.attendance == Attendance.NO_SHOW:
                    continue
                
                #If the player has a lower result (i.e. 1st place instead of 2nd) calculate the updated elo winning score
                elif match_player.match_result.value[1] < match_opponent.match_result.value[1]:
                    expected_score = EloCalculation.probabilistic_elo(player.current_elo, opponent.current_elo)
                    elo_change = K_FACTOR * (MATCH_WIN - expected_score[0])
                    counter += 1
                    elo_delta += elo_change

                #If the player has a bigger result (i.e. 2nd place instead of 1st) calculate the updated elo losing score
                elif match_player.match_result.value[1] > match_opponent.match_result.value[1]:
                    expected_score = EloCalculation.probabilistic_elo(player.current_elo, opponent.current_elo)
                    elo_change = K_FACTOR * (MATCH_LOSE - expected_score[0])
                    counter += 1
                    elo_delta += elo_change

                #If the player has the sameresult (i.e. tie) calculate the updated elo draw score score
                elif match_player.match_result.value[1] == match_opponent.match_result.value[1]:
                    expected_score = EloCalculation.probabilistic_elo(player.current_elo, opponent.current_elo)
                    elo_change = K_FACTOR * (MATCH_DRAW - expected_score[0])
                    counter += 1
                    elo_delta += elo_change

            # if there are no opponents skip the calculating logic
            if counter == 0:
                continue
            # We divide elo_delta by the number of players to scale winnings down to the number of total opponents
            elo_delta = elo_delta/counter

            #Add the elo_delta from all match results to the player's current elo
            elo_update[player.player_id] = elo_delta

            # new loop to apply elo wins, draws and losses to all players using the items() function
        for player_id, value in elo_update.items(): 

            #for all players in player_list check if the id is equal and then apply elo changes
            for p in players_list:
                if p.player_id == player_id: 
                    p.current_elo += value

        # We return the updated players list and the elo_calculations for future audit logs
        return (players_list, elo_update)
