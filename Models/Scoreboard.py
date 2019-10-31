from abc import ABCMeta, abstractmethod
from copy import deepcopy
from datetime import datetime, time
from ..Utils import (Databasable, Downloadable, Fileable, Observable, Serializable,
                        Updatable)


################################################################################
################################################################################


yahooUrl = "https://sports.yahoo.com"
def yId(item):
    return item.split(".")[-1]


################################################################################
################################################################################


class Scoreboard(metaclass=ABCMeta):

    _info = {}
    _newGame = {"away_id":-1,
                "home_id":-1,
                "game_id":-1,
                "game_time":None,
                "status":None,
                "url":None}

    def __init__(self):
        self.info = deepcopy(self._info)


################################################################################
################################################################################


class NFLScoreboard(Scoreboard, Downloadable, Fileable,
                        Observable, Serializable, Updatable):

    _info = {
                "season": -1,
                "season_type": 2,
                "week": -1,
                "games": [],
                "next_update": datetime.today()
            }


    def __init__(self, model, season, season_type, week):
        super().__init__()

        self.model = model


    # Downloadable methods
    def getUrl(self, **kwargs):
        return "https://sports.yahoo.com/nfl/scoreboard/?confId=&scoreboardSeason={0[season]}&schedState={0[season_type]}&dateRange={0[week]}".format(kwargs)


    def parseData(self, data):
        info = {}
        stores = data["context"]["dispatcher"]["stores"]
        pageData = stores["PageStore"]["pageData"]["entityData"]
        leagueAbrv = pageData["leagueId"]
        queryData = stores["ClientStore"]["currentRoute"]["query"]
        gamesData = stores["GamesStore"]

        info["season"] = queryData["scoreboardSeason"]
        info["season_type"] = queryData["schedState"]
        info["week"] = queryData["dateRange"]
        for game in [value for key, value in gamesData.items() if leagueAbrv in key]:
            newGame = deepcopy(self._newGame)
            newGame["away_id"] = yId(game["away_team_id"])
            newGame["home_id"] = yId(game["home_team_id"])
            newGame["game_id"] = yId(game["gameid"])
            newGame["game_time"] = game["start_time"]
            newGame["status"] = game["status_type"]
            newGame["url"] = yahooUrl + game["navigation_links"]["boxscore"]["url"]
            info["games"].append(newGame)
        return info


    # Fileable methods
    def getFilePath(self):
        return super().getFilePath() + "/NFL/{0[season]}/{0[season_type]}/{0[week]}/scoreboard.json".format(self.info)


    # Serializable methods
    def serialize(self):
        newInfo = {}
        for key, value in self.info.items():
            newInfo[key] = value
        games = []
        for game in self.info["games"]:
            newGame = deepcopy(game)
            newGame["game_time"] = datetime.strftime(game["game_time"], "%a, %d %b %Y %H:%M:%S %z")
            games.append(newGame)
        newInfo["games"] = games
        return newInfo


    def unserialize(self, info):
        for key, value in info.items():
            self.info[key] = value
        for game in self.info["games"]:
            game["game_time"] = datetime.strptime(game["game_time"], "%a, %d %b %Y %H:%M:%S %z")
        self.info["next_update"] = datetime.strptime(info["next_update"], "%Y-%m-%d %H:%M:%S.%f")


    # Observable methods
    def notifyObservers(self):
        super().notifyObservers()
        for observer in self.observers:
            observer.update(self.info)


    def isChanged(self, info):
        changed = False
        for key, value in [(key, value) for key, value in  self.info.items() if key != "next_update"]:
            if info.get(key, None) != value:
                changed = True
                break
        return changed


    # Updatable methods
    def nextUpdate(self):
        return self.info["next_update"]


    def update(self):
        data = self.downloadItem()
        info = self.parseData(data)
        self.unserialize(info)
        self.info["next_update"] = datetime.today() + timedelta(1)
        self.isChanged(info)
        if
