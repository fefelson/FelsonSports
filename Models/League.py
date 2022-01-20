import datetime

from abc import ABCMeta, abstractmethod
from pprint import pprint
from sqlite3 import IntegrityError


################################################################################
################################################################################





################################################################################
################################################################################


class League(metaclass=ABCMeta):

    _dbManager = None
    _boxScore = None
    _fileManager = None
    _info = {
                "leagueId": "n/a",
                "slugId": "n/a",
                "lastUpdate": None,
                "currentSeason": None,
                "startDate": None,
                "endDate": None,
                "playoffs": None,
                "allStar": None,
                "weeks": None
            }

    _matchup = None
    _player = None
    _reportManager = None
    _schedule = None
    _team = None


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.isActive = False
        self.boxScore = self._boxScore(self._info["leagueId"])
        self.dbManager = self._dbManager()
        self.fileManager = self._fileManager(self._info)
        self.matchup = self._matchup(self)
        self.player = self._player(self)
        self.report = self._reportManager(self)
        self.schedule = self._schedule(self)
        # self.team = self._team(self)

        self.setActive()

        print("\n\n\n")


    def printLeagueInfo(self):
        print("\n----------League------------")
        pprint(self.fileManager.info)
        print("----------------------")


    def setActive(self):
        today = datetime.datetime.today()
        # print(today)
        # print(datetime.datetime.strptime(self.settings["startDate"], "%Y-%m-%d"))
        # print(datetime.datetime.strptime(self.settings["endDate"], "%Y-%m-%d"))
        if (today >= datetime.datetime.strptime(self.fileManager.info["startDate"], "%Y-%m-%d")
            and today <= datetime.datetime.strptime(self.fileManager.info["endDate"], "%Y-%m-%d")):
            self.isActive = True
            self.printLeagueInfo()


    def update(self):
        if self.fileManager.checkUpdate():
            self.dbManager.openDB()
            for newDate in self.fileManager.determineUpdates():
                for gameInfo in self.schedule.getGames(newDate):
                    self.boxScore.create(gameInfo)
                    print("inserting game into db\n")
                    try:
                        self.dbManager.insertGame(self.boxScore.getInfo())
                        self.dbManager.commit()
                    except IntegrityError:
                        print("insertGame IntegrityError")
                self.fileManager.update(newDate)
            self.report.create()

            try:
                for playerId in self.dbManager.unknownPlayers():
                    try:
                        self.player.create(playerId)
                        self.dbManager.insertPlayer(self.player.getInfo())
                        self.dbManager.commit()
                    except KeyError:
                        print("KeyError")
                    except IntegrityError:
                        print("insertPlayer IntegrityError")
            except TypeError:
                print("None type not iterable")
            self.dbManager.closeDB()


        self.dbManager.openDB()
        matchDate = self.fileManager.determineMatchDate()
        for gameInfo in self.schedule.getMatchup(matchDate):
            try:
                self.matchup.create(gameInfo)
            except TypeError:
                pass
        self.dbManager.closeDB()




################################################################################
################################################################################
