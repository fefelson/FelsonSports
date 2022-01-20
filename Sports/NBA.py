from ..DB import NBADB
from ..Models import (DailyBoxScore, DailyFileManager, DailyMatchup, DailySchedule,
                        NBAPlayer, League, NBAReport)




################################################################################
################################################################################

currentSeason = 2021

################################################################################
################################################################################



class NBA(League):

    _boxScore = DailyBoxScore
    _dbManager = NBADB
    _fileManager = DailyFileManager
    _info = {
                "leagueId": "nba",
                "slugId": "nba",
                "lastUpdate": "2021-10-19",
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
