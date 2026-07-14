K_FACTOR = 30

class EloCalculation:
    @staticmethod
    def probabilistic_elo(rating_a, rating_b):
        win_probabilityA =1.0 / (1 + (10**((rating_b - rating_a)/400)))
        win_probabilityB = 1 - win_probabilityA
        return (win_probabilityA, win_probabilityB)
