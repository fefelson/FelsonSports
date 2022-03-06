from ..DB import WNBADB
from ..Models import (DailyBoxScore, DailyFileManager, DailyMatchup, DailySchedule,
                        NBAPlayer, League, NBAReport)




################################################################################
################################################################################

currentSeason = 2021

################################################################################
################################################################################



class WNBA(League):

    _boxScore = DailyBoxScore
    _dbManager = WNBADB
    _fileManager = DailyFileManager
    _info = {
                "leagueId": "wnba",
                "slugId": "wnba",
                "lastUpdate": "2020-04-26",
                "currentSeason": currentSeason,
                "startDate": "2021-10-19",
                "playoffs": "2022-04-11",
                "endDate": "2022-06-20",
                "allStar": "2022-02-20"
            }
    _matchup = DailyMatchup
    _player = NBAPlayer
    _reportManager = NBAReport
    _schedule = DailySchedule



    def __init__(self, *args, **kwargs):
        print("NBA constructor")
        super().__init__(*args, **kwargs)
