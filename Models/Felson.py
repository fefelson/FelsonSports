from ..Sports import NBA, MLB, NCAAB, NFL, NCAAF


class Felson:

    def __init__(self, ):

        self.leagues = dict([(league.getInfo()["leagueId"], league) for league in [league() for league in (NBA, MLB, NCAAB, NFL, NCAAF)] if league.isActive])

        for key, value in self.leagues.items():
