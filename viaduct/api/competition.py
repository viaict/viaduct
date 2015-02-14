import math


class CompetitionAPI:
    @staticmethod
    def expected_score(Ra, Rb):
        return 1.0 / (1.0 + math.pow(10.0, (Ra - Rb) / 400.0))
