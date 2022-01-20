from ..DB import NCAABDB
from ..Models import (DailyBoxScore, DailyFileManager, DailyMatchup, DailySchedule,
                        NCAABPlayer, League, NCAABReport)



################################################################################
################################################################################

currentSeason = 2021

################################################################################
################################################################################


class NCAAB(League):

    _boxScore = DailyBoxScore
    _dbManager = NCAABDB
    _fileManager = DailyFileManager
    _info = {
                "leagueId": "ncaab",
                "slugId": "college-basketball",
                "lastUpdate": "2021-11-07",
                "currentSeason": currentSeason,
                "startDate": "2021-11-08",
                "playoffs": "2022-03-14",
                "endDate": "2022-04-06",
                "allStar": "2022-07-13"
            }
    _matchup = DailyMatchup
    _player = NCAABPlayer
    _reportManager = NCAABReport
    _schedule = DailySchedule


    def __init__(self, *args, **kwargs):
        print("NCAAB constructor")
        super().__init__(*args, **kwargs)
