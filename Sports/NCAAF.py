from ..DB import NCAAFDB
from ..Models import (League, NCAAFPlayer, NCAAFReport, WeeklyBoxScore, WeeklyFileManager,
                        WeeklyMatchup, WeeklySchedule)

################################################################################
################################################################################


currentSeason = 2021

################################################################################
################################################################################


class NCAAF(League):

    _boxScore = WeeklyBoxScore
    _dbManager = NCAAFDB
    _fileManager = WeeklyFileManager
    _info = {
                "leagueId": "ncaaf",
                "slugId": "college-football",
                "lastUpdate": "2021-11-25",
                "updateWeek": "12",
                "currentSeason": currentSeason,
                "startDate": "2021-08-22",
                "playoffs": "2022-01-11",
                "endDate": "2022-02-01",
                "finalWeek": "16",
                "allStar": "2022-02-06",
                "weeks": (
                            (("2021-08-22", "2021-08-29", "0"),
                            ("2021-08-30", "2021-09-07", "1"),
                            ("2021-09-08", "2021-09-12", "2"),
                            ("2021-09-13", "2021-09-20", "3"),
                            ("2021-09-21", "2021-09-26", "4"),
                            ("2021-09-27", "2021-10-03", "5"),
                            ("2021-10-04", "2021-10-10", "6"),
                            ("2021-10-11", "2021-10-17", "7"),
                            ("2021-10-18", "2021-10-24", "8"),
                            ("2021-10-25", "2021-10-31", "9"),
                            ("2021-11-01", "2021-11-07", "10"),
                            ("2021-11-08", "2021-11-14", "11"),
                            ("2021-11-15", "2021-11-21", "12"),
                            ("2021-11-22", "2021-11-28", "13"),
                            ("2021-11-29", "2021-12-05", "14"),
                            ("2021-12-06", "2021-12-12", "15"),
                            ("2021-12-13", "2021-12-20", "16")
                                                                )
                        )
            }
    _matchup = WeeklyMatchup
    _player = NCAAFPlayer
    _reportManager = NCAAFReport
    _schedule = WeeklySchedule


    def __init__(self, *args, **kwargs):
        print("NCAAF constructor")
        super().__init__(*args, **kwargs)
