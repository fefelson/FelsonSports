from abc import ABCMeta, abstractmethod
from copy import deepcopy
from datetime import datetime
from ..Utils import Databasable, Downloadable, Serializable, Updatable


################################################################################
################################################################################


class League(metaclass=ABCMeta):

    _info = {
                "name": "N/A",
                "abrv": "N/A",
                "current_season": "N/A",
                "start_date": "N/A",
                "end_date": "N/A",
                "season_phase": "offseason",
                "next_update": "N/A",
                "is_active": False
            }

    def __init__(self):
        self.info = deepcopy(self._info)


################################################################################
################################################################################


class NFLLeague(League, Databasable, Downloadable, Serializable, Updatable):

    def __init__(self, model):
        super().__init__()

        self.model = model

    # Databasable methods
    def getDB(self):
        return self.model.getDB("nfl")


    def getDBTable(self):
        return "league"


    def getTableItems(self):
        return self.model.getDBItems("nfl", "league")


    def getTablePK(self):
        return "league_id"


    def getItemId(self):
        return 1

    # Downloadable methods
    def getUrl(self, **kwargs):
        return "https://sports.yahoo.com/nfl/standings/"


    def parseData(self, data):
        info = {}
        stores = data["context"]["dispatcher"]["stores"]
        pageData = stores["PageStore"]["pageData"]["entityData"]
        leagueAbrv = pageData["leagueId"]
        leagueData = stores["LeaguesStore"][leagueAbrv]

        info["current_season"] = pageData["year"]
        info["abrv"] = leagueAbrv
        info["season_phase"] = pageData["currentSeasonPhase"]
        info["name"] = pageData["displayName"]
        info["start_date"] = leagueData["season_phases"]["2"]["phase_start"]
        return info


    # Serializable methods
    def serialize(self):
        newInfo = {}
        for key, value in self.info.items():
            newInfo[key] = value
        newInfo["start_date"] = str(newInfo["start_date"])
        newInfo["end_date"] = str(newInfo["end_date"])
        newInfo["next_update"] = str(newInfo["next_update"])
        return newInfo


    def unserialize(self, info):
        for key, value in info.items():
            self.info[key] = value

        self.info["start_date"] = datetime.strptime(info["start_date"], "%Y-%m-%d %H:%M:%S.%f")
        self.info["end_date"] = datetime.strptime(info["end_date"], "%Y-%m-%d %H:%M:%S.%f")
        self.info["next_update"] = datetime.strptime(info["next_update"], "%Y-%m-%d %H:%M:%S.%f")


    def nextUpdate(self):
        return self.info["next_update"]


    def update(self):
        data = self.downloadItem()
        info = self.parseData(data)
        self.unserialize(info)


################################################################################
################################################################################


class MLBLeague(League, Databasable, Downloadable, Serializable, Updatable):

    def __init__(self, model):
        super().__init__()

        self.model = model

    # Databasable methods
    def getDB(self):
        return self.model.getDB("mlb")


    def getDBTable(self):
        return "league"


    def getTableItems(self):
        return self.model.getDBItems("mlb", "league")


    def getTablePK(self):
        return "league_id"


    def getItemId(self):
        return 1

    # Downloadable methods
    def getUrl(self):
        return "https://sports.yahoo.com/mlb/standings/"


    def parseData(self, data):
        info = {}
        stores = data["context"]["dispatcher"]["stores"]
        pageData = stores["PageStore"]["pageData"]["entityData"]
        leagueAbrv = pageData["leagueId"]
        leagueData = stores["LeaguesStore"][leagueAbrv]

        info["current_season"] = pageData["year"]
        info["abrv"] = leagueAbrv
        info["season_phase"] = pageData["currentSeasonPhase"]
        info["name"] = pageData["displayName"]
        return info


    # Serializable methods
    def serialize(self):
        newInfo = {}
        for key, value in self.info.items():
            newInfo[key] = value
        newInfo["start_date"] = str(newInfo["start_date"])
        newInfo["end_date"] = str(newInfo["end_date"])
        newInfo["next_update"] = str(newInfo["next_update"])
        return newInfo


    def unserialize(self, info):
        for key, value in info.items():
            self.info[key] = value

        self.info["start_date"] = datetime.strptime(info["start_date"], "%Y-%m-%d %H:%M:%S.%f")
        self.info["end_date"] = datetime.strptime(info["end_date"], "%Y-%m-%d %H:%M:%S.%f")
        self.info["next_update"] = datetime.strptime(info["next_update"], "%Y-%m-%d %H:%M:%S.%f")


    def nextUpdate(self):
        return self.info["next_update"]


    def update(self):
        data = self.downloadItem()
        info = self.parseData(data)
        self.unserialize(info)


################################################################################
################################################################################


class NBALeague(League, Databasable, Downloadable, Serializable, Updatable):

    def __init__(self, model):
        super().__init__()

        self.model = model

    # Databasable methods
    def getDB(self):
        return self.model.getDB("nba")


    def getDBTable(self):
        return "league"


    def getTableItems(self):
        return self.model.getDBItems("nba", "league")


    def getTablePK(self):
        return "league_id"


    def getItemId(self):
        return 1

    # Downloadable methods
    def getUrl(self):
        return "https://sports.yahoo.com/nba/standings/"


    def parseData(self, data):
        info = {}
        stores = data["context"]["dispatcher"]["stores"]
        pageData = stores["PageStore"]["pageData"]["entityData"]
        leagueAbrv = pageData["leagueId"]
        leagueData = stores["LeaguesStore"][leagueAbrv]

        info["current_season"] = pageData["year"]
        info["abrv"] = leagueAbrv
        info["season_phase"] = pageData["currentSeasonPhase"]
        info["name"] = pageData["displayName"]
        return info


    # Serializable methods
    def serialize(self):
        newInfo = {}
        for key, value in self.info.items():
            newInfo[key] = value
        newInfo["start_date"] = str(newInfo["start_date"])
        newInfo["end_date"] = str(newInfo["end_date"])
        newInfo["next_update"] = str(newInfo["next_update"])
        return newInfo


    def unserialize(self, info):
        for key, value in info.items():
            self.info[key] = value

        self.info["start_date"] = datetime.strptime(info["start_date"], "%Y-%m-%d %H:%M:%S.%f")
        self.info["end_date"] = datetime.strptime(info["end_date"], "%Y-%m-%d %H:%M:%S.%f")
        self.info["next_update"] = datetime.strptime(info["next_update"], "%Y-%m-%d %H:%M:%S.%f")


    def nextUpdate(self):
        return self.info["next_update"]


    def update(self):
        data = self.downloadItem()
        info = self.parseData(data)
        self.unserialize(info)


################################################################################
################################################################################
